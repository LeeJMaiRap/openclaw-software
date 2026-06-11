#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = REPO_ROOT / "tasks"
VAULT_ROOT = REPO_ROOT / "vaults" / "openclaw-ai"
TASK_MD_DIR = VAULT_ROOT / "01-tasks"
OUTPUT_DIR = VAULT_ROOT / "02-outputs"
LOG_DIR = VAULT_ROOT / "03-logs"


def batch_task_ids(batch_id: str) -> list[str]:
    ids: list[str] = []
    for path in sorted(TASKS_DIR.glob("TASK-*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if data.get("batch_id") == batch_id:
            ids.append(data.get("task_id") or path.stem)
    return ids


def candidate_paths(batch_id: str) -> list[Path]:
    task_ids = batch_task_ids(batch_id)
    paths: list[Path] = []
    for task_id in task_ids:
        paths.extend([
            TASKS_DIR / f"{task_id}.json",
            TASK_MD_DIR / f"{task_id}.md",
            OUTPUT_DIR / f"{task_id}-output.md",
            LOG_DIR / f"{task_id}-done.md",
            LOG_DIR / f"{task_id}-dispatch.md",
        ])
    paths.extend(LOG_DIR.glob(f"{batch_id}-*.md"))
    paths.extend(LOG_DIR.glob(f"{batch_id}-*.json"))
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        if path.exists() and path not in seen:
            seen.add(path)
            unique.append(path)
    return unique


def main() -> int:
    parser = argparse.ArgumentParser(description="List or remove generated artifacts for a LeeJ batch.")
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--mode", choices=("list", "delete"), default="list")
    args = parser.parse_args()

    paths = candidate_paths(args.batch_id)
    if not paths:
        print(f"No artifacts found for {args.batch_id}")
        return 0

    for path in paths:
        print(path.relative_to(REPO_ROOT))

    if args.mode == "delete":
        for path in paths:
            path.unlink(missing_ok=True)
        print(f"Deleted {len(paths)} artifacts for {args.batch_id}")
    else:
        print(f"Listed {len(paths)} artifacts for {args.batch_id}; use --mode delete to remove")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
