#!/usr/bin/env python3
"""LeeJ Worker Dispatcher: prepare OpenClaw agentTurn dispatch payloads."""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = REPO_ROOT / "tasks"
LOG_DIR = REPO_ROOT / "vaults" / "openclaw-ai" / "03-logs"
OUTPUT_DIR = REPO_ROOT / "vaults" / "openclaw-ai" / "02-outputs"

MODEL_BY_WORKER = {
    "claude-cli": "gpt-gmn-token-tunel/cx/gpt-5.5",
    "codex-cli": "gpt-gmn-token-tunel/cx/gpt-5.4",
    "hermes": "gpt-gmn-token-tunel/cx/gpt-5.4",
}
PROJECT_WORKER_ROLE_BY_WORKER = {
    "claude-cli": "worker-code",
    "codex-cli": "worker-code",
    "hermes": "worker-hermes",
}
DISPLAY_MODEL_PREFIX = "gpt-gmn-token-tunel/"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def display_model(model: str) -> str:
    return model[len(DISPLAY_MODEL_PREFIX):] if model.startswith(DISPLAY_MODEL_PREFIX) else model


def load_task(path: Path) -> dict[str, Any]:
    try:
        task = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"❌ Lỗi: Không tìm thấy task file: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"❌ Lỗi: JSON không hợp lệ dòng {exc.lineno}, cột {exc.colno}: {exc.msg}")

    required = [
        "task_id", "project", "goal", "acceptance_criteria", "constraints",
        "worker", "timeout_minutes", "depends_on",
    ]
    for field in required:
        if field not in task:
            raise SystemExit(f"❌ Lỗi: Thiếu field bắt buộc: {field}")
    return task


def task_path(task_id: str) -> Path:
    return TASKS_DIR / f"{task_id}.json"


def worker_message(task: dict[str, Any]) -> str:
    task_id = task["task_id"]
    criteria = "\n".join(f"{i}. {item}" for i, item in enumerate(task["acceptance_criteria"], 1))
    constraints = "\n".join(f"- {item}" for item in task["constraints"])
    depends_on = task.get("depends_on", [])
    deps = ", ".join(depends_on) if depends_on else "none"
    return f"""[OpenClaw Worker Task]

Task ID: {task_id}
Project: {task['project']}
Batch ID: {task.get('batch_id', 'N/A')}
Depends on: {deps}

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

IMPORTANT: All output files must be written to absolute path:
/data/workspace/openclaw-ai/
Example:
- output → /data/workspace/openclaw-ai/vaults/openclaw-ai/02-outputs/{task_id}-output.md
- done log → /data/workspace/openclaw-ai/vaults/openclaw-ai/03-logs/{task_id}-done.md
"""


def build_dispatch(task: dict[str, Any], path: Path) -> dict[str, Any]:
    task_id = task["task_id"]
    worker = task["worker"]
    session_name = f"worker-{task_id}"
    project_id = task.get("discord_project_id") or os.environ.get("OPENCLAW_DISCORD_PROJECT_ID")
    if worker == "manual":
        return {
            "task_id": task_id,
            "worker": worker,
            "model": None,
            "sessionTarget": None,
            "sessionName": None,
            "timeoutSeconds": None,
            "message": None,
            "taskPath": str(path),
            "manualPath": f"vaults/openclaw-ai/01-tasks/{task_id}.md",
        }
    if worker not in MODEL_BY_WORKER:
        raise SystemExit(f"❌ Lỗi: Worker không hỗ trợ: {worker}")
    model = MODEL_BY_WORKER[worker]
    timeout_seconds = int(task["timeout_minutes"]) * 60
    message = worker_message(task)
    project_worker_role = PROJECT_WORKER_ROLE_BY_WORKER.get(worker)
    session_key = None
    if project_id and project_worker_role:
        session_key = f"agent:software:project-{project_id}-{project_worker_role}"
    return {
        "task_id": task_id,
        "worker": worker,
        "model": model,
        "sessionTarget": f"session:{session_name}" if session_key is None else None,
        "sessionName": session_name if session_key is None else session_key,
        "sessionKey": session_key,
        "timeoutSeconds": timeout_seconds,
        "message": message,
        "taskPath": str(path),
        "dispatchMethod": "sessions_send" if session_key else "cron",
        "sessionsSend": {
            "sessionKey": session_key,
            "message": message,
            "timeoutSeconds": timeout_seconds,
        } if session_key else None,
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
- Dispatch method: {dispatch.get('dispatchMethod', 'cron')}
- Session key: {dispatch.get('sessionKey') or 'N/A'}
- Task file: `{Path(dispatch['taskPath']).as_posix()}`
- Spawn status: {spawn_status}
"""
    if job_id:
        content += f"- Cron job id: {job_id}\n"
    if dispatch["worker"] == "manual":
        content += f"\n## Manual handling\n\nCheck: `{dispatch['manualPath']}`\n"
    else:
        content += "\n## AgentTurn message\n\n```text\n" + dispatch["message"] + "```\n"
        if dispatch.get("dispatchMethod") == "sessions_send":
            content += "\n## sessions_send payload\n\n```json\n" + json.dumps(dispatch["sessionsSend"], ensure_ascii=False, indent=2) + "\n```\n"
        else:
            content += "\n## Cron payload\n\n```json\n" + json.dumps(dispatch["cronPayload"], ensure_ascii=False, indent=2) + "\n```\n"
    log_path.write_text(content, encoding="utf-8")
    return log_path


def acquire_lock(lock_path: Path, timeout_seconds: int = 5) -> int:
    start = time.time()
    while True:
        try:
            return os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            if time.time() - start > timeout_seconds:
                try:
                    if time.time() - lock_path.stat().st_mtime > 60:
                        lock_path.unlink()
                        continue
                except FileNotFoundError:
                    continue
                raise SystemExit(f"❌ Lỗi: Không lấy được lockfile: {lock_path}")
            time.sleep(0.1)


def append_batch_log(batch_id: str, text: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"{batch_id}-batch.md"
    lock_path = LOG_DIR / f"{batch_id}-batch.md.lock"
    fd = acquire_lock(lock_path)
    try:
        os.write(fd, f"pid={os.getpid()}\n".encode("utf-8"))
        with log_path.open("a", encoding="utf-8") as f:
            f.write(text)
    finally:
        os.close(fd)
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def load_batch_tasks(batch_id: str) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for path in sorted(TASKS_DIR.glob("TASK-*.json")):
        task = load_task(path)
        if task.get("batch_id") == batch_id:
            task["_path"] = path
            tasks.append(task)
    if not tasks:
        raise SystemExit(f"❌ Lỗi: Không tìm thấy task cho batch_id {batch_id}")
    return tasks


def validate_graph(tasks: list[dict[str, Any]]) -> None:
    ids = {task["task_id"] for task in tasks}
    for task in tasks:
        for dep in task.get("depends_on", []):
            if dep not in ids:
                raise SystemExit(f"❌ Lỗi: {task['task_id']} depends_on ngoài batch: {dep}")

    visiting: set[str] = set()
    visited: set[str] = set()
    deps_by_id = {task["task_id"]: task.get("depends_on", []) for task in tasks}

    def visit(task_id: str) -> None:
        if task_id in visiting:
            raise SystemExit(f"❌ Lỗi: dependency graph có cycle tại {task_id}")
        if task_id in visited:
            return
        visiting.add(task_id)
        for dep in deps_by_id[task_id]:
            visit(dep)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in ids:
        visit(task_id)


def compute_waves(tasks: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    remaining = {task["task_id"]: task for task in tasks}
    done: set[str] = set()
    waves: list[list[dict[str, Any]]] = []
    while remaining:
        ready = [task for task in remaining.values() if set(task.get("depends_on", [])).issubset(done)]
        if not ready:
            raise SystemExit("❌ Lỗi: Không thể tạo wave từ dependency graph")
        ready.sort(key=lambda task: task["task_id"])
        waves.append(ready)
        for task in ready:
            done.add(task["task_id"])
            remaining.pop(task["task_id"])
    return waves



def build_dispatch_plan(batch_id: str, waves: list[list[dict[str, Any]]], timeout_minutes: int) -> dict[str, Any]:
    plan_waves: list[dict[str, Any]] = []
    for index, wave in enumerate(waves, 1):
        plan_tasks: list[dict[str, Any]] = []
        for task in wave:
            path = task.get("_path", task_path(task["task_id"]))
            dispatch = build_dispatch(task, Path(path))
            plan_tasks.append({
                "task_id": task["task_id"],
                "worker": task["worker"],
                "sessionTarget": dispatch.get("sessionTarget"),
                "sessionName": dispatch.get("sessionName"),
                "sessionKey": dispatch.get("sessionKey"),
                "dispatchMethod": dispatch.get("dispatchMethod"),
                "model": dispatch.get("model"),
                "timeoutSeconds": dispatch.get("timeoutSeconds"),
                "message": dispatch.get("message"),
                "taskPath": str(path),
                "depends_on": task.get("depends_on", []),
                "cronPayload": dispatch.get("cronPayload"),
                "sessionsSend": dispatch.get("sessionsSend"),
            })
        plan_waves.append({"wave": index, "tasks": plan_tasks})
    return {
        "batch_id": batch_id,
        "timeout_minutes": timeout_minutes,
        "poll_interval_seconds": 15,
        "status": "prepared",
        "waves": plan_waves,
    }


def write_dispatch_plan(batch_id: str, plan: dict[str, Any]) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    plan_path = LOG_DIR / f"{batch_id}-dispatch-plan.json"
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return plan_path


def poll_wave(job_ids: list[str], timeout_minutes: int) -> dict[str, Any]:
    """Runtime polling contract for Sprint 3.

    Python dispatcher cannot call the OpenClaw cron tool directly. The OpenClaw
    runtime wrapper must poll cron run history for each job id every 15 seconds
    until every job reaches ok/error, or until timeout_minutes expires.
    """
    if not job_ids:
        raise ValueError("job_ids must not be empty")
    if timeout_minutes <= 0:
        raise ValueError("timeout_minutes must be positive")
    return {
        "done": False,
        "ok": 0,
        "error": 0,
        "timeout": False,
        "poll_interval_seconds": 15,
        "timeout_minutes": timeout_minutes,
        "jobs": {
            job_id: {
                "status": "pending",
                "summary": "Waiting for OpenClaw runtime cron run history polling.",
                "durationMs": None,
            }
            for job_id in job_ids
        },
    }


def append_wave_result_log(batch_id: str, wave_index: int, task_results: list[dict[str, Any]], status: str) -> None:
    title_by_status = {
        "done": "done",
        "error": "completed with errors",
        "timeout": "timeout",
    }
    title = title_by_status.get(status, status)
    lines = [f"## Wave {wave_index} {title}\n\n", f"- Timestamp: {utc_now()}\n"]
    for result in task_results:
        duration = result.get("durationMs")
        duration_text = f" | duration: {duration / 1000:.1f}s" if isinstance(duration, int) else ""
        summary = result.get("summary")
        summary_text = f" | summary: {summary}" if summary else ""
        lines.append(
            f"- {result['task_id']} → {result.get('sessionName', 'N/A')} | "
            f"status: {result.get('status', 'unknown')} | cron status: {result.get('cronStatus', 'unknown')}"
            f"{duration_text}{summary_text}\n"
        )
    lines.append("\n")
    append_batch_log(batch_id, "".join(lines))

def run_single(task_file: str) -> int:
    path = Path(task_file)
    if not path.is_absolute():
        path = REPO_ROOT / path
    task = load_task(path)
    dispatch = build_dispatch(task, path)
    write_log(dispatch)
    if dispatch["worker"] == "manual":
        print(f"⏸ {dispatch['task_id']} cần xử lý thủ công. Kiểm tra:")
        print(dispatch["manualPath"])
        return 0
    print(json.dumps(dispatch, ensure_ascii=False, indent=2))
    print(f"✅ Dispatch payload ready: {dispatch['sessionName']} | model: {display_model(dispatch['model'])}")
    return 0


def run_batch(batch_id: str) -> int:
    tasks = load_batch_tasks(batch_id)
    validate_graph(tasks)
    waves = compute_waves(tasks)
    batch_timeout = max(int(task["timeout_minutes"]) for task in tasks)
    total = len(tasks)

    plan = build_dispatch_plan(batch_id, waves, batch_timeout)
    plan_path = write_dispatch_plan(batch_id, plan)

    log_path = LOG_DIR / f"{batch_id}-batch.md"
    if log_path.exists():
        log_path.unlink()
    append_batch_log(batch_id, f"# {batch_id} — Batch dispatch log\n\n- Created at: {utc_now()}\n- Tasks: {total}\n- Batch timeout minutes: {batch_timeout}\n- Dispatch plan: `{plan_path.relative_to(REPO_ROOT)}`\n- Poll interval seconds: 15\n- Runtime note: Python prepared only; no cron jobs spawned by this command.\n\n")

    dispatched = 0
    for index, wave in enumerate(waves, 1):
        prefix = f"🚀 Batch {batch_id}: dispatching wave {index} ({len(wave)} tasks)" if index == 1 else f"🚀 dispatching wave {index} ({len(wave)} task{'s' if len(wave) != 1 else ''})"
        print(prefix)
        append_batch_log(batch_id, f"## Wave {index} prepared\n\n- Timestamp: {utc_now()}\n- Task count: {len(wave)}\n\n")
        for task in wave:
            path = task.get("_path", task_path(task["task_id"]))
            dispatch = build_dispatch(task, Path(path))
            write_log(dispatch)
            append_batch_log(batch_id, f"- {task['task_id']} → {dispatch.get('sessionName')} | {display_model(dispatch['model']) if dispatch.get('model') else 'manual'} | status: prepared\n")
            print(f"   → {dispatch['sessionName']} | {display_model(dispatch['model'])}")
            dispatched += 1
        append_batch_log(batch_id, "\n")
        print(f"⏳ Polling wave {index}...")
    print(f"✅ Batch {batch_id} prepared: {dispatched}/{total} tasks")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare OpenClaw worker dispatch payloads.")
    parser.add_argument("task_file", nargs="?", help="Path to task JSON file.")
    parser.add_argument("--batch", dest="batch_id", help="Prepare dispatch waves for a batch id.")
    args = parser.parse_args()

    if args.batch_id:
        return run_batch(args.batch_id)
    if not args.task_file:
        print("❌ Lỗi: Cần task file hoặc --batch B-xxx")
        return 2
    return run_single(args.task_file)


if __name__ == "__main__":
    raise SystemExit(main())
