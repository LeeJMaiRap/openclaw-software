#!/usr/bin/env python3
"""Fix request queue helpers for LeeJ runtime mediation.

Python cannot call OpenClaw sessions_send directly. The runtime assistant reads pending
requests with this helper, calls sessions_send as a tool, then marks status.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
FIX_DIR = REPO_ROOT / "vaults" / "openclaw-ai" / "03-logs" / "fix-requests"

def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def save(path: Path, data: dict[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)

def pending() -> list[tuple[Path, dict[str, Any]]]:
    FIX_DIR.mkdir(parents=True, exist_ok=True)
    items: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted(FIX_DIR.glob("TASK-*-fix.json")):
        data = load(path)
        if data.get("status") == "pending":
            items.append((path, data))
    return items

def mark(task_id: str, status: str, note: str = "", worker_reply: str = "") -> Path:
    path = FIX_DIR / f"{task_id}-fix.json"
    data = load(path)
    data["status"] = status
    data["updated_at"] = utc_now()
    if note:
        data["note"] = note
    if worker_reply:
        data["worker_reply"] = worker_reply
    save(path, data)
    return path

def cmd_pending() -> int:
    items = pending()
    print(json.dumps([data for _, data in items], ensure_ascii=False, indent=2))
    return 0

def cmd_message(task_id: str) -> int:
    path = FIX_DIR / f"{task_id}-fix.json"
    data = load(path)
    print(data["message"])
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(description="Fix request queue helper.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("pending")
    msg = sub.add_parser("message")
    msg.add_argument("task_id")
    mk = sub.add_parser("mark")
    mk.add_argument("task_id")
    mk.add_argument("status", choices=["pending", "done", "failed"])
    mk.add_argument("--note", default="")
    mk.add_argument("--worker-reply", default="")
    args = parser.parse_args()
    if args.cmd == "pending":
        return cmd_pending()
    if args.cmd == "message":
        return cmd_message(args.task_id)
    if args.cmd == "mark":
        path = mark(args.task_id, args.status, args.note, args.worker_reply)
        print(path.relative_to(REPO_ROOT))
        return 0
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
