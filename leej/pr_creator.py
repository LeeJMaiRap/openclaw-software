#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = REPO_ROOT / "tasks"
VAULT_ROOT = REPO_ROOT / "vaults" / "openclaw-ai"
OUTPUT_DIR = VAULT_ROOT / "02-outputs"
LOG_DIR = VAULT_ROOT / "03-logs"
TASK_VAULT_DIR = VAULT_ROOT / "01-tasks"


def run(cmd: list[str], *, check: bool = True, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(cmd)}\n{result.stdout}")
    return result


def load_task(task_id: str) -> dict[str, Any]:
    path = TASKS_DIR / f"{task_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"task file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def slugify_goal(goal: str, max_words: int = 5) -> str:
    words = re.findall(r"[a-zA-Z0-9À-ỹ]+", goal.lower())[:max_words]
    asciiish = []
    for word in words:
        word = (
            word.replace("đ", "d")
            .replace("Đ", "d")
        )
        safe = re.sub(r"[^a-z0-9]+", "", word)
        if safe:
            asciiish.append(safe)
    slug = "-".join(asciiish) or "task"
    return re.sub(r"-+", "-", slug).strip("-")[:60]


def branch_name(task_id: str, goal: str) -> str:
    return f"task/{task_id}-{slugify_goal(goal)}"


def title_for(task_id: str, goal: str) -> str:
    return f"[{task_id}] {goal}"


def body_for(task: dict[str, Any], batch_id: str | None, project: str | None) -> str:
    criteria = task.get("acceptance_criteria", [])
    lines = [
        f"Task: `{task['task_id']}`",
        f"Batch: `{batch_id or task.get('batch_id', 'N/A')}`",
        f"Project: `{project or task.get('project', 'N/A')}`",
        "",
        "## Goal",
        "",
        str(task.get("goal", "")),
        "",
        "## Acceptance criteria",
        "",
    ]
    if criteria:
        lines.extend(f"- [x] {item}" for item in criteria)
    else:
        lines.append("- [ ] No acceptance criteria listed")
    lines.extend([
        "",
        "## Verification",
        "",
        f"- [x] `python3 leej/checker.py tasks/{task['task_id']}.json`",
    ])
    return "\n".join(lines)


def paths_from_done_log(task_id: str) -> list[Path]:
    done_log = LOG_DIR / f"{task_id}-done.md"
    if not done_log.exists():
        return []
    text = done_log.read_text(encoding="utf-8", errors="replace")
    paths: list[Path] = []
    for raw in re.findall(r"/data/workspace/openclaw-ai/[A-Za-z0-9_./-]+", text):
        path = Path(raw.rstrip(".,`)"))
        try:
            path.relative_to(REPO_ROOT)
        except ValueError:
            continue
        if path.exists() and path.is_file():
            paths.append(path)
    return paths


def related_paths(task_id: str, batch_id: str | None) -> list[Path]:
    paths = [
        TASKS_DIR / f"{task_id}.json",
        TASK_VAULT_DIR / f"{task_id}.md",
        OUTPUT_DIR / f"{task_id}-output.md",
        LOG_DIR / f"{task_id}-done.md",
        *paths_from_done_log(task_id),
    ]
    if batch_id:
        paths.extend([
            LOG_DIR / f"{batch_id}-batch.md",
            LOG_DIR / f"{batch_id}-dispatch-plan.json",
            LOG_DIR / f"{batch_id}-pipeline.md",
            LOG_DIR / f"{batch_id}-runtime-actions.json",
            LOG_DIR / f"{batch_id}-check.md",
        ])
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        if path.exists() and path not in seen:
            seen.add(path)
            unique.append(path)
    return unique


def ensure_checker_pass(task_id: str) -> None:
    result = run(["python3", "leej/checker.py", f"tasks/{task_id}.json"], check=False)
    if result.returncode != 0:
        raise RuntimeError(f"checker failed for {task_id}; PR not created\n{result.stdout}")


def current_branch() -> str:
    return run(["git", "branch", "--show-current"]).stdout.strip() or "main"


def unique_branch(base: str) -> str:
    exists = run(["git", "rev-parse", "--verify", base], check=False)
    if exists.returncode != 0:
        return base
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"{base}-{stamp}"


def create_pr(task_id: str, batch_id: str | None, project: str | None, dry_run: bool = False) -> str:
    task = load_task(task_id)
    ensure_checker_pass(task_id)
    base_branch = current_branch()
    target_branch = unique_branch(branch_name(task_id, str(task.get("goal", "task"))))
    paths = related_paths(task_id, batch_id or task.get("batch_id"))
    if not paths:
        raise RuntimeError(f"no related files found for {task_id}")

    title = title_for(task_id, str(task.get("goal", "")))
    body = body_for(task, batch_id, project)
    rel_paths = [str(path.relative_to(REPO_ROOT)) for path in paths]

    if dry_run:
        print(json.dumps({
            "task_id": task_id,
            "branch": target_branch,
            "title": title,
            "paths": rel_paths,
            "body": body,
        }, ensure_ascii=False, indent=2))
        return "DRY_RUN"

    with tempfile.TemporaryDirectory(prefix=f"openclaw-pr-{task_id}-") as tmp_name:
        worktree = Path(tmp_name) / "repo"
        try:
            run(["git", "worktree", "add", "-b", target_branch, str(worktree), "main"])
        except Exception:
            run(["git", "worktree", "add", "-b", target_branch, str(worktree), "origin/main"])

        try:
            for rel in rel_paths:
                src = REPO_ROOT / rel
                dst = worktree / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

            run(["git", "add", *rel_paths], cwd=worktree)
            diff = run(["git", "diff", "--cached", "--quiet"], check=False, cwd=worktree)
            if diff.returncode == 0:
                raise RuntimeError(f"no staged changes for {task_id}; PR not created")
            summary = str(task.get("goal", "")).strip().split(".")[0][:80]
            run(["git", "commit", "-m", f"feat: {task_id} — {summary}"], cwd=worktree)
            run(["git", "push", "origin", target_branch], cwd=worktree)
            pr = run([
                "gh", "pr", "create",
                "--title", title,
                "--body", body,
                "--base", "main",
                "--head", target_branch,
            ], cwd=worktree)
            url = pr.stdout.strip().splitlines()[-1]
            print(url)
            return url
        finally:
            run(["git", "worktree", "remove", "--force", str(worktree)], check=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create GitHub PR for a checked OpenClaw task.")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--batch-id")
    parser.add_argument("--project")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        create_pr(args.task_id, args.batch_id, args.project, args.dry_run)
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"PR_CREATE_FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
