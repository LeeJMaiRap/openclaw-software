#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = REPO_ROOT / "vaults" / "openclaw-ai" / "03-logs"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run(cmd: list[str], *, timeout: int | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )


def load_actions(batch_id: str) -> dict[str, Any]:
    path = LOG_DIR / f"{batch_id}-runtime-actions.json"
    if not path.exists():
        raise FileNotFoundError(f"runtime actions not found: {path.relative_to(REPO_ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def extract_pr_urls(output: str) -> list[str]:
    urls = re.findall(r"https://github\.com/[^\s)]+/pull/\d+", output)
    seen: set[str] = set()
    unique: list[str] = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique.append(url)
    return unique


def worker_command(job: dict[str, Any]) -> list[str]:
    payload = job.get("payload") or {}
    session_key = payload.get("sessionKey") or job.get("sessionKey")
    message = payload.get("message")
    timeout_seconds = int(payload.get("timeoutSeconds") or job.get("timeoutSeconds") or 900)
    model = job.get("model")
    if not session_key or not message:
        raise ValueError(f"invalid sessions_send job for {job.get('task_id')}: missing sessionKey/message")
    cmd = [
        "openclaw",
        "agent",
        "--session-key",
        session_key,
        "--message",
        message,
        "--timeout",
        str(timeout_seconds),
        "--json",
    ]
    if model:
        cmd.extend(["--model", model])
    return cmd


def append_md(lines: list[str], text: str = "") -> None:
    lines.append(text)


def execute_runtime(batch_id: str, project: str | None = None, auto_pr: bool = False) -> int:
    actions = load_actions(batch_id)
    md_lines: list[str] = [
        f"# {batch_id} runtime execution",
        "",
        f"Started: {utc_now()}",
        f"Project: {project or 'N/A'}",
        "",
    ]
    json_log: dict[str, Any] = {
        "batch_id": batch_id,
        "project": project,
        "started_at": utc_now(),
        "waves": [],
        "checker": None,
        "prs": [],
        "status": "running",
    }

    failed = False
    for wave in actions.get("waves", []):
        wave_no = wave.get("wave")
        append_md(md_lines, f"## Wave {wave_no}")
        wave_log = {"wave": wave_no, "jobs": []}
        for job in wave.get("jobs", []):
            task_id = job.get("task_id", "unknown")
            method = job.get("dispatchMethod")
            append_md(md_lines, f"### {task_id}")
            if method != "sessions_send":
                msg = f"unsupported dispatchMethod={method}"
                append_md(md_lines, f"❌ {msg}")
                wave_log["jobs"].append({"task_id": task_id, "ok": False, "error": msg})
                failed = True
                break
            try:
                cmd = worker_command(job)
                started = time.time()
                result = run(cmd, timeout=int(job.get("timeoutSeconds") or 1800) + 60)
                elapsed = round(time.time() - started, 2)
                ok = result.returncode == 0
                append_md(md_lines, f"Command exit: `{result.returncode}`")
                append_md(md_lines, f"Elapsed seconds: `{elapsed}`")
                append_md(md_lines, "")
                append_md(md_lines, "```text")
                append_md(md_lines, (result.stdout or "").strip())
                append_md(md_lines, "```")
                wave_log["jobs"].append({
                    "task_id": task_id,
                    "ok": ok,
                    "returncode": result.returncode,
                    "elapsed_seconds": elapsed,
                    "output": result.stdout,
                })
                if not ok:
                    failed = True
                    break
            except Exception as exc:  # noqa: BLE001
                append_md(md_lines, f"❌ {type(exc).__name__}: {exc}")
                wave_log["jobs"].append({"task_id": task_id, "ok": False, "error": f"{type(exc).__name__}: {exc}"})
                failed = True
                break
        json_log["waves"].append(wave_log)
        append_md(md_lines, "")
        if failed:
            append_md(md_lines, "Stopped because a wave job failed.")
            break

    if failed:
        json_log["status"] = "worker_failed"
    else:
        append_md(md_lines, "## Checker")
        checker = run([sys.executable, "leej/checker.py", "--batch", batch_id, "--auto-pr"], timeout=300)
        append_md(md_lines, f"Command exit: `{checker.returncode}`")
        append_md(md_lines, "")
        append_md(md_lines, "```text")
        append_md(md_lines, (checker.stdout or "").strip())
        append_md(md_lines, "```")
        json_log["checker"] = {"returncode": checker.returncode, "output": checker.stdout}
        if checker.returncode != 0:
            json_log["status"] = "checker_failed"
        else:
            json_log["status"] = "checker_passed"
            if auto_pr:
                ready_tasks = re.findall(r"^PR_READY_TASK=(TASK-\d+)$", checker.stdout or "", flags=re.MULTILINE)
                append_md(md_lines, "")
                append_md(md_lines, "## Pull requests")
                for task_id in ready_tasks:
                    cmd = [sys.executable, "leej/pr_creator.py", "--task-id", task_id, "--batch-id", batch_id]
                    if project:
                        cmd.extend(["--project", project])
                    pr_result = run(cmd, timeout=600)
                    urls = extract_pr_urls(pr_result.stdout or "")
                    ok = pr_result.returncode == 0 and bool(urls)
                    json_log["prs"].append({
                        "task_id": task_id,
                        "ok": ok,
                        "returncode": pr_result.returncode,
                        "urls": urls,
                        "output": pr_result.stdout,
                    })
                    append_md(md_lines, f"### {task_id}")
                    append_md(md_lines, f"Command exit: `{pr_result.returncode}`")
                    if pr_result.returncode != 0:
                        append_md(md_lines, "⚠️ PR creation failed; runtime continues.")
                    for url in urls:
                        append_md(md_lines, f"🔗 PR: {url}")
                    append_md(md_lines, "")
                    append_md(md_lines, "```text")
                    append_md(md_lines, (pr_result.stdout or "").strip())
                    append_md(md_lines, "```")
                json_log["status"] = "pr_created" if any(pr.get("ok") for pr in json_log["prs"]) else "pr_failed"

    json_log["finished_at"] = utc_now()
    md_path = LOG_DIR / f"{batch_id}-runtime-execution.md"
    json_path = LOG_DIR / f"{batch_id}-runtime-execution.json"
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    json_path.write_text(json.dumps(json_log, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Runtime status: {json_log['status']}")
    print(f"Runtime log: {md_path.relative_to(REPO_ROOT)}")
    print(f"Runtime JSON: {json_path.relative_to(REPO_ROOT)}")
    if json_log.get("checker"):
        print((json_log["checker"].get("output") or "").strip())
    for pr in json_log.get("prs", []):
        for url in pr.get("urls", []):
            print(f"🔗 PR: {url}")

    return 0 if json_log["status"] in {"checker_passed", "pr_created", "pr_failed"} else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute OpenClaw runtime actions for a prepared LeeJ batch.")
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--project")
    parser.add_argument("--auto-pr", action="store_true")
    args = parser.parse_args()
    try:
        return execute_runtime(args.batch_id, project=args.project, auto_pr=args.auto_pr)
    except Exception as exc:  # noqa: BLE001
        print(f"RUNTIME_EXECUTOR_FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
