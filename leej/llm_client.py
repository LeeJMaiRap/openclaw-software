#!/usr/bin/env python3
"""Simple stdlib-only LLM client for LeeJ Agent via 9Router/OpenClaw config."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_MODEL = "gpt-gmn-token-tunel/cx/gpt-5.4"
DEFAULT_TIMEOUT = 60.0
DEFAULT_CONFIG_PATH = Path(os.environ.get("OPENCLAW_CONFIG", "/data/.openclaw/openclaw.json"))


class LLMClientError(RuntimeError):
    """Raised when the LLM client cannot complete a request."""


def load_config(config_path: Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise LLMClientError(f"config not found: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise LLMClientError(
            f"invalid JSON in {config_path}: line {exc.lineno} col {exc.colno}: {exc.msg}"
        ) from exc


def split_model(model: str) -> tuple[str, str]:
    if "/" not in model:
        raise LLMClientError(f"model must include provider prefix: {model}")
    provider_name, provider_model = model.split("/", 1)
    if not provider_name or not provider_model:
        raise LLMClientError(f"invalid model format: {model}")
    return provider_name, provider_model


def get_provider(config: dict[str, Any], provider_name: str) -> dict[str, Any]:
    provider = config.get("models", {}).get("providers", {}).get(provider_name)
    if not isinstance(provider, dict):
        raise LLMClientError(f"provider not found in config: {provider_name}")
    if not provider.get("baseUrl"):
        raise LLMClientError(f"provider baseUrl missing: {provider_name}")
    if not provider.get("apiKey"):
        raise LLMClientError(f"provider apiKey missing: {provider_name}")
    return provider


def extract_content(response_body: str) -> str:
    try:
        payload = json.loads(response_body)
    except json.JSONDecodeError as exc:
        raise LLMClientError(f"non-JSON response: {response_body[:500]}") from exc

    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise LLMClientError(f"response missing choices: {response_body[:500]}")

    first = choices[0]
    if not isinstance(first, dict):
        raise LLMClientError(f"response choice is not object: {response_body[:500]}")

    message = first.get("message")
    if not isinstance(message, dict):
        raise LLMClientError(f"response missing choices[0].message: {response_body[:500]}")

    content = message.get("content")
    if not isinstance(content, str):
        raise LLMClientError(f"response missing choices[0].message.content: {response_body[:500]}")

    return content


def complete(
    prompt: str,
    model: str = DEFAULT_MODEL,
    timeout: float = DEFAULT_TIMEOUT,
    config_path: Path = DEFAULT_CONFIG_PATH,
    temperature: float = 0.2,
    max_tokens: int = 2048,
) -> str:
    config = load_config(config_path)
    provider_name, provider_model = split_model(model)
    provider = get_provider(config, provider_name)

    base_url = str(provider["baseUrl"]).rstrip("/")
    api_key = str(provider["apiKey"])
    url = f"{base_url}/chat/completions"

    body = {
        "model": provider_model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response_body = response.read(2_000_000).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        error_body = exc.read(4096).decode("utf-8", errors="replace")
        raise LLMClientError(f"HTTP {exc.code}: {error_body[:1000]}") from exc
    except Exception as exc:
        raise LLMClientError(f"request failed: {type(exc).__name__}: {exc}") from exc

    return extract_content(response_body)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Call 9Router chat completions using OpenClaw config.")
    parser.add_argument("prompt", help="Prompt to send to the model")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Full model id, default: {DEFAULT_MODEL}")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help="Request timeout in seconds")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH, help="OpenClaw config path")
    parser.add_argument("--temperature", type=float, default=0.2, help="Sampling temperature")
    parser.add_argument("--max-tokens", type=int, default=2048, help="Max output tokens")
    args = parser.parse_args(argv)

    try:
        content = complete(
            prompt=args.prompt,
            model=args.model,
            timeout=args.timeout,
            config_path=args.config,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
        )
    except LLMClientError as exc:
        print(f"❌ llm_client failed: {exc}", file=sys.stderr)
        return 2

    print(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
