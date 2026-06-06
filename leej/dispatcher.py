#!/usr/bin/env python3
"""LeeJ Worker Dispatcher Sprint 1: prepare OpenClaw agentTurn dispatch payload."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = REPO_ROOT / "vaults" / "openclaw-ai" / "03-logs"
TASK_LOG_DIR = REPO_ROOT / "vaults" / "openclaw-ai" / "01-tasks"

MODEL_BY_WORKER = {
    "claude-cli": "gpt-gmn-token-tunel/cx/gpt-5.3-codex",
    "codex-cli": "gpt-gmn-token-tunel/cx/gpt-5.3-codex-high",
    "hermes": "gpt-gmn-token-tunel/cx/gpt-5.4",
}

DISPLAY_MODEL_PREFIX = "gpt-gmn-token-tunel/"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def display_model(model: str) -> str:
    if model.startswith(DISPLAY_MODEL_PREFIX):
        return model[len(DISPLAY_MODEL_PREFIX):]
    return model


def load_task(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            task = json.load(f)
    except FileNotFoundError:
        raise SystemExit(f"❌ Lỗi: Không tìm thấy task file: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"❌ Lỗi: JSON không hợp lệ dòng {exc.lineno}, cột {exc.colno}: {exc.msg}")

    required = ["task_id", "project", "goal", "acceptance_criteria", "constraints", "worker", "timeout_minutes"]
    for field in required:
        if field not in task:
            raise SystemExit(f"❌ Lỗi: Thiếu field bắt buộc: {field}")
    return task


def worker_message(task: dict[str, Any]) -> str:
    task_id = task["task_id"]
    criteria = "\n".join(f"{i}. {item}" for i, item in enumerate(task["acceptance_criteria"], 1))
    constraints = "\n".join(f"- {item}" for item in task["constraints"])
    return f"""[OpenClaw Worker Task]

Task ID: {task_id}
Project: {task['project']}

Goal:
{task['goal']}

Acceptance criteria:
{criteria}

Constraints:
{constraints}

Output requirements:
- Write final output to: vaults/openclaw-ai/02-outputs/{task_id}-output.md
- Write completion log to: vaults/openclaw-ai/03-logs/{task_id}-done.md
- Keep response concise and include verification notes.
"""


def build_dispatch(task: dict[str, Any], task_path: Path) -> dict[str, Any]:
    task_id = task["task_id"]
    worker = task["worker"]
    session_name = f"worker-{task_id}"

    if worker == "manual":
        return {
            "task_id": task_id,
            "worker": worker,
            "model": None,
            "sessionTarget": None,
            "sessionName": None,
            "timeoutSeconds": None,
            "message": None,
            "taskPath": str(task_path),
            "manualPath": f"vaults/openclaw-ai/01-tasks/{task_id}.md",
        }

    if worker not in MODEL_BY_WORKER:
        raise SystemExit(f"❌ Lỗi: Worker không hỗ trợ: {worker}")

    model = MODEL_BY_WORKER[worker]
    timeout_seconds = int(task["timeout_minutes"]) * 60
    message = worker_message(task)
    return {
        "task_id": task_id,
        "worker": worker,
        "model": model,
        "sessionTarget": f"session:{session_name}",
        "sessionName": session_name,
        "timeoutSeconds": timeout_seconds,
        "message": message,
        "taskPath": str(task_path),
        "cronPayload": {
            "sessionTarget": f"session:{session_name}",
            "payload": {
                "kind": "agentTurn",
                "model": model,
                "message": message,
                "lightContext": True,
                "timeoutSeconds": timeout_seconds,
            },
        },
    }


def write_log(dispatch: dict[str, Any], spawn_status: str = "prepared", job_id: str | None = None) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    task_id = dispatch["task_id"]
    log_path = LOG_DIR / f"{task_id}-dispatch.md"
    model = dispatch.get("model") or "N/A"
    session_name = dispatch.get("sessionName") or "N/A"
    content = f"""# {task_id} — Dispatch log

## Metadata

- Timestamp: {utc_now()}
- Task ID: {task_id}
- Worker: {dispatch['worker']}
- Model: {model}
- Session name: {session_name}
- Task file: `{Path(dispatch['taskPath']).as_posix()}`
- Spawn status: {spawn_status}
"""
    if job_id:
        content += f"- Cron job id: {job_id}\n"

    if dispatch["worker"] == "manual":
        content += f"\n## Manual handling\n\nCheck: `{dispatch['manualPath']}`\n"
    else:
        content += "\n## AgentTurn message\n\n```text\n" + dispatch["message"] + "```\n"
        content += "\n## Cron payload\n\n```json\n" + json.dumps(dispatch["cronPayload"], ensure_ascii=False, indent=2) + "\n```\n"
    log_path.write_text(content, encoding="utf-8")
    return log_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare an OpenClaw worker dispatch payload.")
    parser.add_argument("task_file", help="Path to task JSON file.")
    args = parser.parse_args()

    task_path = Path(args.task_file)
    if not task_path.is_absolute():
        task_path = REPO_ROOT / task_path

    task = load_task(task_path)
    dispatch = build_dispatch(task, task_path)
    write_log(dispatch)

    if dispatch["worker"] == "manual":
        print(f"⏸ {dispatch['task_id']} cần xử lý thủ công. Kiểm tra:")
        print(dispatch["manualPath"])
        return 0

    print(json.dumps(dispatch, ensure_ascii=False, indent=2))
    print(f"✅ Dispatch payload ready: {dispatch['sessionName']} | model: {display_model(dispatch['model'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
