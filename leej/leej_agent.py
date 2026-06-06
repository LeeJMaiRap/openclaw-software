#!/usr/bin/env python3
"""LeeJ Agent Sprint 1: create a validated worker task from user request.

Usage:
    python3 leej/leej_agent.py "Viết hàm Python tính số Fibonacci thứ n"
    python3 leej/leej_agent.py --file request.txt
    echo "..." | python3 leej/leej_agent.py
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = REPO_ROOT / "tasks"
TASK_LOG_DIR = REPO_ROOT / "vaults" / "openclaw-ai" / "01-tasks"
VALIDATOR = REPO_ROOT / "validators" / "validate_task.py"


CODE_KEYWORDS = [
    "viết hàm",
    "viet ham",
    "code",
    "python",
    "javascript",
    "typescript",
    "api",
    "bug",
    "test",
    "function",
    "implement",
]
ANALYSIS_KEYWORDS = [
    "phân tích",
    "phan tich",
    "so sánh",
    "so sanh",
    "đánh giá",
    "danh gia",
    "lý luận",
    "ly luan",
    "analyze",
    "compare",
    "evaluate",
]
MANUAL_KEYWORDS = [
    "phê duyệt",
    "phe duyet",
    "chờ user",
    "cho user",
    "manual",
    "human",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create an OpenClaw AI task file.")
    parser.add_argument("request", nargs="*", help="User request text.")
    parser.add_argument("--file", dest="file", help="Read request text from file.")
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
        raise ValueError("Yêu cầu rỗng")
    return text


def next_task_id() -> str:
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    max_id = 0
    for path in TASKS_DIR.glob("TASK-*.json"):
        match = re.fullmatch(r"TASK-(\d{3,})\.json", path.name)
        if match:
            max_id = max(max_id, int(match.group(1)))
    return f"TASK-{max_id + 1:03d}"


def classify_worker(request: str) -> tuple[str, str]:
    text = request.lower()
    if any(keyword in text for keyword in MANUAL_KEYWORDS):
        return "manual", "manual"
    if any(keyword in text for keyword in ANALYSIS_KEYWORDS):
        return "hermes", "analysis"
    if any(keyword in text for keyword in CODE_KEYWORDS):
        return "claude-cli", "code"
    return "claude-cli", "code"


def extract_function_name(request: str) -> str:
    lower = request.lower()
    if "fibonacci" in lower:
        return "fibonacci(n)"
    match = re.search(r"(?:hàm|ham|function)\s+([A-Za-z_][A-Za-z0-9_]*)", request)
    if match:
        return f"{match.group(1)}(...)"
    return "hàm hoặc module được yêu cầu"


def acceptance_criteria(request: str, task_type: str) -> list[str]:
    if task_type == "manual":
        return [
            "User cung cấp acceptance criteria cụ thể trước khi task được giao tiếp.",
            "Task được cập nhật lại với worker phù hợp sau khi user xác nhận.",
            "Quyết định hoặc phê duyệt của user được ghi vào Obsidian log.",
        ]

    if task_type == "analysis":
        return [
            "Output có kết luận rõ ràng trả lời trực tiếp yêu cầu phân tích.",
            "Output nêu ít nhất 3 lý do hoặc luận điểm hỗ trợ kết luận.",
            "Output dài tối thiểu 300 từ hoặc có cấu trúc bullet rõ ràng nếu ngắn hơn.",
        ]

    fn = extract_function_name(request)
    if "fibonacci" in request.lower():
        return [
            "Hàm fibonacci(n) trả về đúng giá trị cho n=0, n=1, n=5 và n=10.",
            "Code chạy được không có lỗi runtime.",
            "Output có ví dụ chạy thử và giải thích ngắn cách hoạt động.",
        ]

    return [
        f"{fn} tạo ra kết quả đúng cho ít nhất 3 input ví dụ liên quan đến yêu cầu.",
        "Code chạy được không có lỗi runtime.",
        "Output có ví dụ chạy thử và giải thích ngắn cách hoạt động.",
    ]


def build_task(task_id: str, request: str) -> dict[str, object]:
    worker, task_type = classify_worker(request)
    return {
        "task_id": task_id,
        "project": "openclaw-ai",
        "goal": request,
        "acceptance_criteria": acceptance_criteria(request, task_type),
        "constraints": [
            "Keep the solution simple for Sprint 1.",
            "Write output in Vietnamese unless the task requires another language.",
        ],
        "context_files": [
            "docs/architecture/openclaw_knowledge_base_v2.txt",
        ],
        "worker": worker,
        "priority": "high",
        "timeout_minutes": 30,
    }


def validate_task(path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(path)],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode != 0:
        print(result.stdout.rstrip())
        raise SystemExit(result.returncode)


def write_task_log(task: dict[str, object], request: str, task_path: Path) -> None:
    TASK_LOG_DIR.mkdir(parents=True, exist_ok=True)
    task_id = str(task["task_id"])
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    criteria = "\n".join(f"- {item}" for item in task["acceptance_criteria"])
    constraints = "\n".join(f"- {item}" for item in task["constraints"])
    content = f"""# {task_id} — Task created

## Metadata

- Created at: {now}
- Project: {task['project']}
- Worker: {task['worker']}
- Priority: {task['priority']}
- Timeout: {task['timeout_minutes']} minutes
- Task file: `{task_path.relative_to(REPO_ROOT)}`

## User request

{request}

## Goal

{task['goal']}

## Acceptance criteria

{criteria}

## Constraints

{constraints}
"""
    (TASK_LOG_DIR / f"{task_id}.md").write_text(content, encoding="utf-8")


def main() -> int:
    args = parse_args()
    try:
        request = read_request(args)
    except ValueError as exc:
        print(f"❌ Lỗi: {exc}")
        return 1

    task_id = next_task_id()
    task = build_task(task_id, request)
    task_path = TASKS_DIR / f"{task_id}.json"
    task_path.write_text(json.dumps(task, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    validate_task(task_path)
    write_task_log(task, request, task_path)

    print(f"✅ Task {task_id} đã tạo: tasks/{task_id}.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
