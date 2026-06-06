#!/usr/bin/env python3
"""LeeJ Pipeline runner: prepare one-command batch pipeline handoff."""

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


def run_cmd(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run LeeJ pipeline preparation for a request.")
    parser.add_argument("request", nargs="*", help="User request text.")
    parser.add_argument("--file", dest="file", help="Read request text from file.")
    parser.add_argument("--batch", action="store_true", default=True, help="Generate a batch; default enabled.")
    return parser.parse_args()


def read_request(args: argparse.Namespace) -> str:
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    elif args.request:
        text = " ".join(args.request)
    else:
        text = sys.stdin.read()
    text = text.strip()
    if not text:
        raise SystemExit("❌ Lỗi: Yêu cầu rỗng")
    return text


def parse_batch_id(output: str) -> str:
    match = re.search(r"Batch\s+(B-\d{3,})", output)
    if not match:
        raise SystemExit("❌ Lỗi: Không parse được batch_id từ leej_agent output")
    return match.group(1)


def wave_task_ids(plan: dict[str, Any]) -> list[list[str]]:
    return [[task["task_id"] for task in wave["tasks"]] for wave in plan["waves"]]


def write_runtime_actions(batch_id: str, plan: dict[str, Any]) -> Path:
    actions = {
        "batch_id": batch_id,
        "created_at": utc_now(),
        "status": "prepared",
        "poll_interval_seconds": plan.get("poll_interval_seconds", 15),
        "timeout_minutes": plan["timeout_minutes"],
        "waves": [],
        "checker": {
            "command": ["python3", "leej/checker.py", "--batch", batch_id],
        },
        "report_path": f"vaults/openclaw-ai/03-logs/{batch_id}-pipeline.md",
    }
    for wave in plan["waves"]:
        actions["waves"].append({
            "wave": wave["wave"],
            "jobs": [
                {
                    "task_id": task["task_id"],
                    "name": task["sessionName"],
                    "sessionTarget": task["sessionTarget"],
                    "model": task["model"],
                    "timeoutSeconds": task["timeoutSeconds"],
                    "payload": task["cronPayload"],
                }
                for task in wave["tasks"]
            ],
        })
    path = LOG_DIR / f"{batch_id}-runtime-actions.json"
    path.write_text(json.dumps(actions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def write_pipeline_report(batch_id: str, request: str, plan: dict[str, Any], actions_path: Path, started: float) -> Path:
    duration = time.time() - started
    lines = [
        f"# {batch_id} — Pipeline report",
        "",
        f"- Created at: {utc_now()}",
        "- Status: prepared",
        f"- Duration seconds: {duration:.1f}",
        f"- Runtime actions: `{actions_path.relative_to(REPO_ROOT)}`",
        f"- Dispatch plan: `vaults/openclaw-ai/03-logs/{batch_id}-dispatch-plan.json`",
        "",
        "## Input",
        "",
        request,
        "",
        "## Waves",
        "",
    ]
    for wave in plan["waves"]:
        ids = ", ".join(task["task_id"] for task in wave["tasks"])
        lines.append(f"- Wave {wave['wave']}: {ids}")
    lines.extend([
        "",
        "## Result",
        "",
        "Prepared only. OpenClaw runtime must spawn and poll cron jobs from runtime-actions.json.",
        "",
    ])
    path = LOG_DIR / f"{batch_id}-pipeline.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> int:
    started = time.time()
    args = parse_args()
    request = read_request(args)

    print("═══════════════════════════════════════")
    print("OpenClaw AI — LeeJ Pipeline")
    print("═══════════════════════════════════════")
    print("📋 Generating tasks...")
    gen = run_cmd([sys.executable, "leej/leej_agent.py", "--batch", request])
    print(gen.stdout.rstrip())
    if gen.returncode != 0:
        print("❌ Task generation failed")
        return gen.returncode
    batch_id = parse_batch_id(gen.stdout)

    print("\n🚀 Preparing dispatch plan...")
    disp = run_cmd([sys.executable, "leej/dispatcher.py", "--batch", batch_id])
    print(disp.stdout.rstrip())
    if disp.returncode != 0:
        print("❌ Dispatch preparation failed")
        return disp.returncode

    plan_path = LOG_DIR / f"{batch_id}-dispatch-plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    for idx, ids in enumerate(wave_task_ids(plan), 1):
        print(f"   Wave {idx}: {', '.join(ids)} → ready")

    actions_path = write_runtime_actions(batch_id, plan)
    report_path = write_pipeline_report(batch_id, request, plan, actions_path, started)

    print("\n⏳ Runtime handoff ready:")
    print(f"   {actions_path.relative_to(REPO_ROOT)}")
    print(f"   {report_path.relative_to(REPO_ROOT)}")
    print("═══════════════════════════════════════")
    print(f"✅ Pipeline prepared: Batch {batch_id} — runtime actions ready")
    print(f"Report: {report_path.relative_to(REPO_ROOT)}")
    print("═══════════════════════════════════════")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
