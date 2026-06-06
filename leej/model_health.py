#!/usr/bin/env python3
"""Sprint 4 model health check for LeeJ worker model mapping.

Stdlib only. Checks:
- worker model mapping from leej.dispatcher
- OpenClaw config allowlist: agents.defaults.models
- provider catalog: models.providers[*].models[*].id
- live router call: POST <baseUrl>/chat/completions
- optional full router catalog mode: GET <baseUrl>/models, then probe all models

Writes JSON report to vaults/openclaw-ai/03-logs/model-health.json.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = REPO_ROOT / "vaults" / "openclaw-ai" / "03-logs"
REPORT_PATH = LOG_DIR / "model-health.json"
DEFAULT_CONFIG_PATH = Path(os.environ.get("OPENCLAW_CONFIG", "/data/.openclaw/openclaw.json"))
DEFAULT_PROVIDER_NAME = os.environ.get("OPENCLAW_MODEL_PROVIDER", "gpt-gmn-token-tunel")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_dispatcher_mapping() -> dict[str, str]:
    dispatcher_path = REPO_ROOT / "leej" / "dispatcher.py"
    spec = importlib.util.spec_from_file_location("leej_dispatcher_health", dispatcher_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import dispatcher mapping from {dispatcher_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    mapping = getattr(module, "MODEL_BY_WORKER", None)
    if not isinstance(mapping, dict):
        raise RuntimeError("dispatcher MODEL_BY_WORKER missing or invalid")
    return {str(worker): str(model) for worker, model in mapping.items()}


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise RuntimeError(f"config not found: {path}")
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid JSON in {path}: line {exc.lineno} col {exc.colno}: {exc.msg}")


def get_provider(config: dict[str, Any], provider_name: str) -> dict[str, Any]:
    providers = config.get("models", {}).get("providers", {})
    provider = providers.get(provider_name)
    if not isinstance(provider, dict):
        raise RuntimeError(f"provider not found: {provider_name}")
    return provider


def provider_for_model(config: dict[str, Any], full_model: str) -> tuple[str | None, dict[str, Any] | None, str]:
    providers = config.get("models", {}).get("providers", {})
    if "/" not in full_model:
        return None, None, full_model
    provider_name, short_model = full_model.split("/", 1)
    provider = providers.get(provider_name)
    if isinstance(provider, dict):
        return provider_name, provider, short_model
    return provider_name, None, short_model


def provider_has_model(provider: dict[str, Any] | None, short_model: str) -> bool:
    if not isinstance(provider, dict):
        return False
    for item in provider.get("models", []):
        if isinstance(item, dict) and item.get("id") == short_model:
            return True
    return False


def configured_catalog_ids(provider: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for item in provider.get("models", []):
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            ids.append(item["id"])
    return sorted(set(ids))


def fetch_router_catalog(provider: dict[str, Any], timeout: float) -> tuple[list[str], str]:
    base_url = str(provider.get("baseUrl", "")).rstrip("/")
    api_key = str(provider.get("apiKey", ""))
    if not base_url:
        raise RuntimeError("provider baseUrl missing")
    if not api_key:
        raise RuntimeError("provider apiKey missing")

    url = f"{base_url}/models"
    request = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {api_key}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read(1048576).decode("utf-8", errors="replace")
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"/models returned non-JSON HTTP {response.status}: {raw[:500]}") from exc
    except urllib.error.HTTPError as exc:
        raw = exc.read(4096).decode("utf-8", errors="replace")
        raise RuntimeError(f"GET /models failed HTTP {exc.code}: {raw[:500]}") from exc
    except Exception as exc:
        raise RuntimeError(f"GET /models failed: {type(exc).__name__}: {exc}") from exc

    data = parsed.get("data")
    if not isinstance(data, list):
        raise RuntimeError("/models response missing data list")

    ids: list[str] = []
    for item in data:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            ids.append(item["id"])
    return sorted(set(ids)), url


def live_probe(provider: dict[str, Any], short_model: str, timeout: float) -> tuple[bool, str, float]:
    base_url = str(provider.get("baseUrl", "")).rstrip("/")
    api_key = str(provider.get("apiKey", ""))
    if not base_url:
        return False, "provider baseUrl missing", 0.0
    if not api_key:
        return False, "provider apiKey missing", 0.0

    url = f"{base_url}/chat/completions"
    body = {
        "model": short_model,
        "messages": [
            {"role": "system", "content": "Reply with exactly: OK"},
            {"role": "user", "content": "health check"},
        ],
        "temperature": 0,
        "max_tokens": 8,
    }
    data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    started = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read(65536).decode("utf-8", errors="replace")
            elapsed = time.monotonic() - started
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                return False, f"non-JSON response HTTP {response.status}: {raw[:200]}", elapsed
            choices = parsed.get("choices")
            if isinstance(choices, list) and choices:
                return True, f"HTTP {response.status}; completion returned", elapsed
            return False, f"HTTP {response.status}; no choices in response", elapsed
    except urllib.error.HTTPError as exc:
        elapsed = time.monotonic() - started
        raw = exc.read(4096).decode("utf-8", errors="replace")
        return False, f"HTTP {exc.code}: {raw[:500]}", elapsed
    except Exception as exc:  # noqa: BLE001 - health report should capture exact failure
        elapsed = time.monotonic() - started
        return False, f"{type(exc).__name__}: {exc}", elapsed


def build_result(
    *,
    worker: str | None,
    full_model: str,
    provider_name: str | None,
    provider: dict[str, Any] | None,
    short_model: str,
    allowlist: dict[str, Any],
    catalog_ids: set[str],
    timeout: float,
    require_allowlist: bool,
) -> dict[str, Any]:
    in_allowlist = full_model in allowlist
    in_provider_catalog = short_model in catalog_ids
    live_ok = False
    live_message = "skipped"
    elapsed_ms = 0

    if provider is None:
        live_message = f"provider not found: {provider_name}"
    elif require_allowlist and not in_allowlist:
        live_message = "not in agents.defaults.models allowlist"
    elif not in_provider_catalog:
        live_message = "not in provider model catalog"
    else:
        live_ok, live_message, elapsed = live_probe(provider, short_model, timeout)
        elapsed_ms = int(round(elapsed * 1000))

    healthy = bool((in_allowlist or not require_allowlist) and in_provider_catalog and live_ok)
    result: dict[str, Any] = {
        "model": full_model,
        "provider": provider_name,
        "provider_model": short_model,
        "in_allowlist": in_allowlist,
        "in_provider_catalog": in_provider_catalog,
        "live_probe": {
            "ok": live_ok,
            "elapsed_ms": elapsed_ms,
            "message": live_message,
        },
        "status": "healthy" if healthy else "unhealthy",
    }
    if worker is not None:
        result = {"worker": worker, **result}
    return result


def check_models(timeout: float, config_path: Path) -> dict[str, Any]:
    mapping = load_dispatcher_mapping()
    config = load_json(config_path)
    allowlist = config.get("agents", {}).get("defaults", {}).get("models", {})
    if not isinstance(allowlist, dict):
        allowlist = {}

    results: list[dict[str, Any]] = []
    for worker, full_model in sorted(mapping.items()):
        provider_name, provider, short_model = provider_for_model(config, full_model)
        catalog_ids = set(configured_catalog_ids(provider)) if provider is not None else set()
        results.append(
            build_result(
                worker=worker,
                full_model=full_model,
                provider_name=provider_name,
                provider=provider,
                short_model=short_model,
                allowlist=allowlist,
                catalog_ids=catalog_ids,
                timeout=timeout,
                require_allowlist=True,
            )
        )

    healthy_count = sum(1 for item in results if item["status"] == "healthy")
    report = {
        "created_at": utc_now(),
        "mode": "mapped",
        "config_path": str(config_path),
        "timeout_seconds": timeout,
        "summary": {
            "total": len(results),
            "healthy": healthy_count,
            "unhealthy": len(results) - healthy_count,
        },
        "models": results,
    }
    return report


def check_all_models(timeout: float, config_path: Path, provider_name: str) -> dict[str, Any]:
    config = load_json(config_path)
    provider = get_provider(config, provider_name)
    allowlist = config.get("agents", {}).get("defaults", {}).get("models", {})
    if not isinstance(allowlist, dict):
        allowlist = {}

    catalog_ids, catalog_url = fetch_router_catalog(provider, timeout)
    catalog_set = set(catalog_ids)
    results: list[dict[str, Any]] = []
    for short_model in catalog_ids:
        full_model = f"{provider_name}/{short_model}"
        results.append(
            build_result(
                worker=None,
                full_model=full_model,
                provider_name=provider_name,
                provider=provider,
                short_model=short_model,
                allowlist=allowlist,
                catalog_ids=catalog_set,
                timeout=timeout,
                require_allowlist=False,
            )
        )

    healthy_count = sum(1 for item in results if item["status"] == "healthy")
    report = {
        "created_at": utc_now(),
        "mode": "all",
        "catalog_source": catalog_url,
        "provider": provider_name,
        "config_path": str(config_path),
        "timeout_seconds": timeout,
        "summary": {
            "total": len(results),
            "healthy": healthy_count,
            "unhealthy": len(results) - healthy_count,
        },
        "models": results,
    }
    return report


def print_summary(report: dict[str, Any]) -> None:
    summary = report["summary"]
    print("OpenClaw AI — Model Health")
    print(f"Mode: {report.get('mode', 'mapped')}")
    print(f"Config: {report['config_path']}")
    if "catalog_source" in report:
        print(f"Catalog: {report['catalog_source']}")
    print(f"Timeout: {report['timeout_seconds']}s")
    print(f"Summary: {summary['healthy']}/{summary['total']} healthy, {summary['unhealthy']} unhealthy")
    for item in report["models"]:
        marker = "✅" if item["status"] == "healthy" else "❌"
        probe = item["live_probe"]
        worker = f"{item['worker']} | " if "worker" in item else ""
        print(
            f"{marker} {worker}{item['model']} | {item['status']} | "
            f"allowlist={item['in_allowlist']} catalog={item['in_provider_catalog']} "
            f"live={probe['ok']} {probe['elapsed_ms']}ms | {probe['message']}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check LeeJ worker model health.")
    parser.add_argument("--timeout", type=float, default=15.0, help="per-model live probe timeout in seconds")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH, help="OpenClaw config path")
    parser.add_argument("--all", action="store_true", help="fetch provider /models catalog and probe every model")
    parser.add_argument("--provider", default=DEFAULT_PROVIDER_NAME, help="provider name for --all catalog mode")
    args = parser.parse_args(argv)

    try:
        if args.all:
            report = check_all_models(args.timeout, args.config, args.provider)
        else:
            report = check_models(args.timeout, args.config)
    except RuntimeError as exc:
        print(f"❌ model health failed: {exc}", file=sys.stderr)
        return 2

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print_summary(report)
    print(f"Report: {REPORT_PATH.relative_to(REPO_ROOT)}")
    return 0 if report["summary"]["unhealthy"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
