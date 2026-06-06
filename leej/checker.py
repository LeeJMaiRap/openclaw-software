#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

COMMON_WORDS = {
    "cho", "và", "có", "của", "được", "không", "với", "các", "một", "thứ",
    "the", "and", "for", "with", "output", "code", "hàm", "ngắn"
}


def normalize(text):
    return text.lower()


def tokens(text):
    return [
        t for t in re.findall(r"[a-zA-ZÀ-ỹ0-9_]+", normalize(text))
        if len(t) > 1 and t not in COMMON_WORDS
    ]


def criterion_passed(criterion, output):
    c = normalize(criterion)
    out = normalize(output)

    # Sprint 1: vài rule rõ cho TASK-001 + fallback keyword matching đơn giản.
    if "fibonacci" in c and all(x in out for x in ["fibonacci(0)", "fibonacci(1)", "fibonacci(5)", "fibonacci(10)"]):
        return True
    if "runtime" in c and ("không có lỗi runtime" in out or "code chạy" in out):
        return True
    if "ví dụ" in c and "giải thích" in c and "ví dụ chạy thử" in out and "cách hoạt động" in out:
        return True

    keys = tokens(criterion)
    if not keys:
        return False
    matched = sum(1 for k in keys if k in out)
    return matched >= max(2, int(len(keys) * 0.6))


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 leej/checker.py tasks/TASK-001.json", file=sys.stderr)
        return 2

    task_path = Path(sys.argv[1])
    task = json.loads(task_path.read_text(encoding="utf-8"))

    task_id = task["task_id"]
    project = task.get("project", "openclaw-ai")
    output_path = Path("vaults") / project / "02-outputs" / f"{task_id}-output.md"
    output = output_path.read_text(encoding="utf-8")

    criteria = task.get("acceptance_criteria", [])
    missing = [c for c in criteria if not criterion_passed(c, output)]
    passed = len(criteria) - len(missing)
    total = len(criteria)

    if missing:
        print(f"⚠️ {task_id}: {passed}/{total} criteria passed — thiếu: " + "; ".join(missing))
        return 1

    print(f"✅ {task_id}: {passed}/{total} criteria passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
