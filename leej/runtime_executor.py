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
    return subprocess.run(cmd, cwd=str(REPO_ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)


def load_actions(batch_id: str) -> dict[str, Any]:
    path = LOG_DIR / f"{batch_id}-runtime-actions.json"
    if not path.exists():
        raise FileNotFoundError(f"runtime actions not found: {path.relative_to(REPO_ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def extract_pr_urls(output: str) -> list[str]:
    urls = re.findall(r"https://github\.com/[^\s)]+/pull/\d+", output)
    return list(dict.fromkeys(urls))


def extract_checker_failures(output: str) -> list[str]:
    failures: list[str] = []
    for line in (output or "").splitlines():
        if line.startswith("⚠️ TASK-") or line.startswith("❌ TASK-"):
            failures.append(line.strip())
    return failures


def job_payload(job: dict[str, Any]) -> dict[str, Any]:
    payload = job.get("payload") or {}
    if "payload" in payload and isinstance(payload["payload"], dict):
        return payload["payload"]
    return payload


def worker_command(job: dict[str, Any]) -> list[str]:
    payload = job_payload(job)
    session_key = (job.get("sessionsSend") or {}).get("sessionKey") or job.get("sessionKey") or payload.get("sessionKey")
    message = (job.get("sessionsSend") or {}).get("message") or payload.get("message") or job.get("message")
    timeout_seconds = int((job.get("sessionsSend") or {}).get("timeoutSeconds") or payload.get("timeoutSeconds") or job.get("timeoutSeconds") or 900)
    model = payload.get("model") or job.get("model")
    if not session_key or not message:
        raise ValueError(f"invalid sessions_send job for {job.get('task_id')}: missing sessionKey/message")
    cmd = ["openclaw", "agent", "--session-key", session_key, "--message", message, "--timeout", str(timeout_seconds), "--json"]
    if model:
        cmd.extend(["--model", model])
    return cmd


def append_md(lines: list[str], text: str = "") -> None:
    lines.append(text)


def unsupported_dispatch_message(method: str | None) -> str:
    if method == "cron":
        return (
            "unsupported dispatchMethod=cron. This batch was prepared without project worker session keys. "
            "Run inside a Discord project #leej channel or pass OPENCLAW_DISCORD_PROJECT_ID so dispatcher emits sessions_send jobs."
        )
    return f"unsupported dispatchMethod={method}"


def run_worker_with_retries(job: dict[str, Any], retries: int, retry_delay: int) -> tuple[bool, list[dict[str, Any]]]:
    attempts: list[dict[str, Any]] = []
    timeout = int(job.get("timeoutSeconds") or 1800) + 60
    for attempt in range(1, retries + 2):
        started = time.time()
        try:
            result = run(worker_command(job), timeout=timeout)
            elapsed = round(time.time() - started, 2)
            attempts.append({
                "attempt": attempt,
                "ok": result.returncode == 0,
                "returncode": result.returncode,
                "elapsed_seconds": elapsed,
                "output": result.stdout,
            })
            if result.returncode == 0:
                return True, attempts
        except Exception as exc:  # noqa: BLE001
            elapsed = round(time.time() - started, 2)
            attempts.append({
                "attempt": attempt,
                "ok": False,
                "error": f"{type(exc).__name__}: {exc}",
                "elapsed_seconds": elapsed,
            })
        if attempt <= retries:
            time.sleep(retry_delay)
    return False, attempts


def execute_runtime(
    batch_id: str,
    project: str | None = None,
    auto_pr: bool = False,
    retries: int = 1,
    retry_delay: int = 10,
) -> int:
    actions = load_actions(batch_id)
    md_lines: list[str] = [
        f"# {batch_id} runtime execution",
        "",
        f"Started: {utc_now()}",
        f"Project: {project or 'N/A'}",
        f"Retries: {retries}",
        "",
    ]
    json_log: dict[str, Any] = {
        "batch_id": batch_id,
        "project": project,
        "started_at": utc_now(),
        "waves": [],
        "checker": None,
        "checker_failures": [],
        "prs": [],
        "status": "running",
    }

    failed = False
    for wave in actions.get("waves", []):
        wave_no = wave.get("wave")
        append_md(md_lines, f"## Wave {wave_no}")
        wave_log: dict[str, Any] = {"wave": wave_no, "jobs": []}
        for job in wave.get("jobs", []):
            task_id = job.get("task_id", "unknown")
            method = job.get("dispatchMethod")
            append_md(md_lines, f"### {task_id}")
            if method != "sessions_send":
                msg = unsupported_dispatch_message(method)
                append_md(md_lines, f"❌ {msg}")
                wave_log["jobs"].append({"task_id": task_id, "ok": False, "error": msg})
                failed = True
                break
            ok, attempts = run_worker_with_retries(job, retries=retries, retry_delay=retry_delay)
            for attempt in attempts:
                append_md(md_lines, f"Attempt {attempt['attempt']} exit: `{attempt.get('returncode', 'error')}`")
                append_md(md_lines, f"Elapsed seconds: `{attempt['elapsed_seconds']}`")
                if attempt.get("error"):
                    append_md(md_lines, f"Error: {attempt['error']}")
                append_md(md_lines, "")
                append_md(md_lines, "```text")
                append_md(md_lines, (attempt.get("output") or "").strip())
                append_md(md_lines, "```")
            wave_log["jobs"].append({"task_id": task_id, "ok": ok, "attempts": attempts})
            if not ok:
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
        checker_failures = extract_checker_failures(checker.stdout or "")
        append_md(md_lines, f"Command exit: `{checker.returncode}`")
        if checker_failures:
            append_md(md_lines, "")
            append_md(md_lines, "### Checker failure summary")
            for failure in checker_failures:
                append_md(md_lines, f"- {failure}")
            append_md(md_lines, "")
            append_md(md_lines, "No PR created.")
        append_md(md_lines, "")
        append_md(md_lines, "```text")
        append_md(md_lines, (checker.stdout or "").strip())
        append_md(md_lines, "```")
        json_log["checker"] = {"returncode": checker.returncode, "output": checker.stdout}
        json_log["checker_failures"] = checker_failures
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
                    json_log["prs"].append({"task_id": task_id, "ok": ok, "returncode": pr_result.returncode, "urls": urls, "output": pr_result.stdout})
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
    for failure in json_log.get("checker_failures", []):
        print(f"CHECKER_FAIL: {failure}")
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
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--retry-delay-seconds", type=int, default=10)
    args = parser.parse_args()
    try:
        return execute_runtime(args.batch_id, project=args.project, auto_pr=args.auto_pr, retries=args.retries, retry_delay=args.retry_delay_seconds)
    except Exception as exc:  # noqa: BLE001
        print(f"RUNTIME_EXECUTOR_FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
