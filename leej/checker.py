#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = REPO_ROOT / "tasks"
LOG_DIR = REPO_ROOT / "vaults" / "openclaw-ai" / "03-logs"
OUTPUT_DIR = REPO_ROOT / "vaults" / "openclaw-ai" / "02-outputs"

COMMON_WORDS = {
    "cho", "và", "có", "của", "được", "không", "với", "các", "một", "thứ",
    "the", "and", "for", "with", "output", "code", "hàm", "ngắn", "data",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize(text: str) -> str:
    return text.lower()


def tokens(text: str) -> list[str]:
    return [
        t for t in re.findall(r"[a-zA-ZÀ-ỹ0-9_]+", normalize(text))
        if len(t) > 1 and t not in COMMON_WORDS
    ]


def criterion_passed(criterion: str, output: str, done_log: str = "") -> bool:
    c = normalize(criterion)
    out = normalize(output + "\n" + done_log)

    if "fibonacci" in c and all(x in out for x in ["fibonacci(0)", "fibonacci(1)", "fibonacci(5)", "fibonacci(10)"]):
        return True
    if "runtime" in c and ("không có lỗi runtime" in out or "code chạy" in out or "ok" in out):
        return True
    if "ví dụ" in c and "giải thích" in c and ("ví dụ" in out and ("giải thích" in out or "cách hoạt động" in out)):
        return True

    # Sprint 2 statistical functions and tests.
    if "tinh_trung_binh" in c and "tinh_trung_binh" in out:
        if "2.0" in out or "5.0" in out or "unittest" in out or "ok" in out:
            return True
    if "tinh_trung_vi" in c and "tinh_trung_vi" in out:
        if "2" in out or "2.5" in out or "unittest" in out or "ok" in out:
            return True
    if "tinh_do_lech_chuan" in c and "tinh_do_lech_chuan" in out:
        if "population" in out or "unittest" in out or "ok" in out:
            return True
    if "danh sách rỗng" in c and ("valueerror" in out or "rỗng" in out):
        return True
    if "population" in c or "sample" in c:
        return "population" in out or "sample" in out
    if "test suite" in c or "unit test" in c:
        return "unittest" in out and "ok" in out

    keys = tokens(criterion)
    if not keys:
        return False
    matched = sum(1 for k in keys if k in out)
    return matched >= max(2, int(len(keys) * 0.6))


def load_task(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check_task(task: dict) -> dict:
    task_id = task["task_id"]
    project = task.get("project", "openclaw-ai")
    output_path = REPO_ROOT / "vaults" / project / "02-outputs" / f"{task_id}-output.md"
    done_path = REPO_ROOT / "vaults" / project / "03-logs" / f"{task_id}-done.md"

    errors: list[str] = []
    output = ""
    done_log = ""
    if output_path.exists():
        output = output_path.read_text(encoding="utf-8")
    else:
        errors.append(f"missing output file: {output_path.relative_to(REPO_ROOT)}")
    if done_path.exists():
        done_log = done_path.read_text(encoding="utf-8")
    else:
        errors.append(f"missing done log: {done_path.relative_to(REPO_ROOT)}")

    criteria = task.get("acceptance_criteria", [])
    missing = [c for c in criteria if not criterion_passed(c, output, done_log)]
    passed = len(criteria) - len(missing)
    total = len(criteria)
    ok = not errors and not missing
    return {
        "task_id": task_id,
        "ok": ok,
        "passed": passed,
        "total": total,
        "missing": missing,
        "errors": errors,
        "output_path": output_path,
        "done_path": done_path,
    }


def print_task_result(result: dict) -> None:
    task_id = result["task_id"]
    if result["ok"]:
        print(f"✅ {task_id}: {result['passed']}/{result['total']} criteria passed")
        return
    details = []
    if result["errors"]:
        details.extend(result["errors"])
    if result["missing"]:
        details.append("thiếu: " + "; ".join(result["missing"]))
    print(f"⚠️ {task_id}: {result['passed']}/{result['total']} criteria passed — " + " | ".join(details))


def load_batch_tasks(batch_id: str) -> list[dict]:
    tasks = []
    for path in sorted(TASKS_DIR.glob("TASK-*.json")):
        task = load_task(path)
        if task.get("batch_id") == batch_id:
            tasks.append(task)
    if not tasks:
        raise SystemExit(f"❌ Lỗi: Không tìm thấy task cho batch_id {batch_id}")
    return tasks


def write_batch_check_log(batch_id: str, results: list[dict]) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for r in results if r["ok"])
    total = len(results)
    lines = [
        f"# {batch_id} — Batch check log",
        "",
        f"- Timestamp: {utc_now()}",
        f"- Result: {passed}/{total} tasks passed",
        "",
        "## Task results",
        "",
    ]
    for result in results:
        status = "passed" if result["ok"] else "failed"
        lines.append(f"### {result['task_id']} — {status}")
        lines.append("")
        lines.append(f"- Criteria: {result['passed']}/{result['total']}")
        lines.append(f"- Output: `{result['output_path'].relative_to(REPO_ROOT)}`")
        lines.append(f"- Done log: `{result['done_path'].relative_to(REPO_ROOT)}`")
        if result["errors"]:
            lines.append("- Errors:")
            lines.extend(f"  - {item}" for item in result["errors"])
        if result["missing"]:
            lines.append("- Missing criteria:")
            lines.extend(f"  - {item}" for item in result["missing"])
        lines.append("")
    path = LOG_DIR / f"{batch_id}-check.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def run_single(task_file: str) -> int:
    task_path = Path(task_file)
    if not task_path.is_absolute():
        task_path = REPO_ROOT / task_path
    result = check_task(load_task(task_path))
    print_task_result(result)
    return 0 if result["ok"] else 1


def run_batch(batch_id: str, auto_pr: bool = False) -> int:
    tasks = load_batch_tasks(batch_id)
    results = [check_task(task) for task in tasks]
    for result in results:
        print_task_result(result)
    path = write_batch_check_log(batch_id, results)
    passed = sum(1 for r in results if r["ok"])
    total = len(results)
    all_passed = passed == total
    if all_passed:
        print(f"✅ Batch {batch_id}: {passed}/{total} tasks passed")
    else:
        print(f"⚠️ Batch {batch_id}: {passed}/{total} tasks passed")
    print(f"📝 Check log: {path.relative_to(REPO_ROOT)}")
    if auto_pr and all_passed:
        print(f"PR_READY_BATCH={batch_id}")
        for task in tasks:
            print(f"PR_READY_TASK={task['task_id']}")
    return 0 if all_passed else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Check task outputs against acceptance criteria.")
    parser.add_argument("task_file", nargs="?", help="Path to task JSON file.")
    parser.add_argument("--batch", dest="batch_id", help="Check all tasks in batch id.")
    parser.add_argument(
        "--auto-pr",
        action="store_true",
        help="If batch is fully passing, print PR_READY_* markers for caller automation.",
    )
    args = parser.parse_args()

    if args.batch_id:
        return run_batch(args.batch_id, auto_pr=args.auto_pr)
    if not args.task_file:
        print("Usage: python3 leej/checker.py tasks/TASK-001.json", file=sys.stderr)
        print("   or: python3 leej/checker.py --batch B-001", file=sys.stderr)
        return 2
    return run_single(args.task_file)


if __name__ == "__main__":
    raise SystemExit(main())
