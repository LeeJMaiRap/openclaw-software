#!/usr/bin/env python3
"""LeeJ Agent: create validated OpenClaw AI task files.

Usage:
    python3 leej/leej_agent.py "Viết hàm Python tính số Fibonacci thứ n"
    python3 leej/leej_agent.py --batch "Xây dựng module thống kê..."
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
    parser = argparse.ArgumentParser(description="Create OpenClaw AI task files.")
    parser.add_argument("request", nargs="*", help="User request text.")
    parser.add_argument("--file", dest="file", help="Read request text from file.")
    parser.add_argument("--batch", action="store_true", help="Split a larger request into a batch of task files.")
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


def existing_task_numbers() -> list[int]:
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    numbers: list[int] = []
    for path in TASKS_DIR.glob("TASK-*.json"):
        match = re.fullmatch(r"TASK-(\d{3,})\.json", path.name)
        if match:
            numbers.append(int(match.group(1)))
    return numbers


def next_task_id() -> str:
    numbers = existing_task_numbers()
    max_id = max(numbers) if numbers else 0
    return f"TASK-{max_id + 1:03d}"


def next_task_ids(count: int) -> list[str]:
    numbers = existing_task_numbers()
    start = (max(numbers) if numbers else 0) + 1
    return [f"TASK-{num:03d}" for num in range(start, start + count)]


def next_batch_id() -> str:
    max_id = 0
    for path in TASKS_DIR.glob("TASK-*.json"):
        try:
            task = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        batch_id = task.get("batch_id")
        if isinstance(batch_id, str):
            match = re.fullmatch(r"B-(\d{3,})", batch_id)
            if match:
                max_id = max(max_id, int(match.group(1)))
    return f"B-{max_id + 1:03d}"


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
            "Keep the solution simple for Sprint 2.",
            "Write output in Vietnamese unless the task requires another language.",
        ],
        "context_files": [
            "docs/architecture/openclaw_knowledge_base_v2.txt",
        ],
        "worker": worker,
        "priority": "high",
        "timeout_minutes": 30,
        "depends_on": [],
    }


def build_function_task(task_id: str, batch_id: str, function_key: str) -> dict[str, object]:
    specs = {
        "mean": {
            "goal": "Viết hàm Python tinh_trung_binh(data) để tính trung bình cộng của danh sách số.",
            "criteria": [
                "Hàm tinh_trung_binh(data) trả về đúng kết quả cho [1, 2, 3] và [2, 4, 6, 8].",
                "Code xử lý danh sách rỗng bằng lỗi hoặc thông báo rõ ràng.",
                "Output có ví dụ chạy thử và giải thích ngắn cách hoạt động.",
            ],
        },
        "median": {
            "goal": "Viết hàm Python tinh_trung_vi(data) để tính trung vị của danh sách số.",
            "criteria": [
                "Hàm tinh_trung_vi(data) trả về đúng kết quả cho danh sách có số phần tử lẻ.",
                "Hàm tinh_trung_vi(data) trả về đúng kết quả cho danh sách có số phần tử chẵn.",
                "Code chạy được không có lỗi runtime và có ví dụ chạy thử.",
            ],
        },
        "stddev": {
            "goal": "Viết hàm Python tinh_do_lech_chuan(data) để tính độ lệch chuẩn của danh sách số.",
            "criteria": [
                "Hàm tinh_do_lech_chuan(data) trả về đúng kết quả cho ít nhất 2 bộ dữ liệu ví dụ.",
                "Code nêu rõ đang tính độ lệch chuẩn population hay sample.",
                "Code chạy được không có lỗi runtime và có ví dụ chạy thử.",
            ],
        },
    }
    spec = specs[function_key]
    return {
        "task_id": task_id,
        "project": "openclaw-ai",
        "goal": spec["goal"],
        "acceptance_criteria": spec["criteria"],
        "constraints": [
            "Keep the solution simple for Sprint 2.",
            "Write output in Vietnamese unless the task requires another language.",
        ],
        "context_files": ["docs/architecture/openclaw_knowledge_base_v2.txt"],
        "worker": "claude-cli",
        "priority": "high",
        "timeout_minutes": 30,
        "depends_on": [],
        "batch_id": batch_id,
    }


def build_test_task(task_id: str, batch_id: str, dependency_ids: list[str]) -> dict[str, object]:
    return {
        "task_id": task_id,
        "project": "openclaw-ai",
        "goal": "Viết unit test cho các hàm thống kê cơ bản: tinh_trung_binh, tinh_trung_vi, tinh_do_lech_chuan.",
        "acceptance_criteria": [
            "Unit test kiểm tra tinh_trung_binh(data) với ít nhất 2 bộ dữ liệu.",
            "Unit test kiểm tra tinh_trung_vi(data) với danh sách có số phần tử chẵn và lẻ.",
            "Unit test kiểm tra tinh_do_lech_chuan(data) với ít nhất 2 bộ dữ liệu và test suite chạy được.",
        ],
        "constraints": [
            "Keep the solution simple for Sprint 2.",
            "Use Python standard library unittest or pytest-style assertions.",
            "Write output in Vietnamese unless the task requires another language.",
        ],
        "context_files": [f"tasks/{dep}.json" for dep in dependency_ids],
        "worker": "claude-cli",
        "priority": "high",
        "timeout_minutes": 30,
        "depends_on": dependency_ids,
        "batch_id": batch_id,
    }



def build_temperature_task(task_id: str, batch_id: str, function_key: str) -> dict[str, object]:
    specs = {
        "c_to_f": {
            "goal": "Viết hàm Python celsius_to_fahrenheit(c) để đổi nhiệt độ từ Celsius sang Fahrenheit.",
            "criteria": [
                "Hàm celsius_to_fahrenheit(c) trả về đúng kết quả cho c=0, c=100 và c=-40.",
                "Code chạy được không có lỗi runtime.",
                "Output có ví dụ chạy thử và giải thích ngắn công thức chuyển đổi.",
            ],
        },
        "f_to_c": {
            "goal": "Viết hàm Python fahrenheit_to_celsius(f) để đổi nhiệt độ từ Fahrenheit sang Celsius.",
            "criteria": [
                "Hàm fahrenheit_to_celsius(f) trả về đúng kết quả cho f=32, f=212 và f=-40.",
                "Code chạy được không có lỗi runtime.",
                "Output có ví dụ chạy thử và giải thích ngắn công thức chuyển đổi.",
            ],
        },
        "c_to_k": {
            "goal": "Viết hàm Python celsius_to_kelvin(c) để đổi nhiệt độ từ Celsius sang Kelvin.",
            "criteria": [
                "Hàm celsius_to_kelvin(c) trả về đúng kết quả cho c=0, c=100 và c=-273.15.",
                "Code chạy được không có lỗi runtime.",
                "Output có ví dụ chạy thử và giải thích ngắn công thức chuyển đổi.",
            ],
        },
    }
    spec = specs[function_key]
    return {
        "task_id": task_id,
        "project": "openclaw-ai",
        "goal": spec["goal"],
        "acceptance_criteria": spec["criteria"],
        "constraints": [
            "Keep the solution simple for Sprint 3.",
            "Write output in Vietnamese unless the task requires another language.",
        ],
        "context_files": ["docs/architecture/openclaw_knowledge_base_v2.txt"],
        "worker": "claude-cli",
        "priority": "high",
        "timeout_minutes": 30,
        "depends_on": [],
        "batch_id": batch_id,
    }


def build_temperature_test_task(task_id: str, batch_id: str, dependency_ids: list[str]) -> dict[str, object]:
    return {
        "task_id": task_id,
        "project": "openclaw-ai",
        "goal": "Viết unit test cho các hàm đổi nhiệt độ: celsius_to_fahrenheit, fahrenheit_to_celsius, celsius_to_kelvin.",
        "acceptance_criteria": [
            "Unit test kiểm tra celsius_to_fahrenheit(c) với c=0, c=100 và c=-40.",
            "Unit test kiểm tra fahrenheit_to_celsius(f) với f=32, f=212 và f=-40.",
            "Unit test kiểm tra celsius_to_kelvin(c) với c=0, c=100 và c=-273.15 và test suite chạy được.",
        ],
        "constraints": [
            "Keep the solution simple for Sprint 3.",
            "Use Python standard library unittest or pytest-style assertions.",
            "Write output in Vietnamese unless the task requires another language.",
        ],
        "context_files": [f"tasks/{dep}.json" for dep in dependency_ids],
        "worker": "claude-cli",
        "priority": "high",
        "timeout_minutes": 30,
        "depends_on": dependency_ids,
        "batch_id": batch_id,
    }

def build_prime_task(task_id: str, batch_id: str) -> dict[str, object]:
    return {
        "task_id": task_id,
        "project": "openclaw-ai",
        "goal": "Viết hàm Python is_prime(n) để kiểm tra một số nguyên có phải số nguyên tố hay không.",
        "acceptance_criteria": [
            "Hàm is_prime(n) trả về False cho n < 2, gồm n=0, n=1 và số âm.",
            "Hàm is_prime(n) trả về True cho các số nguyên tố ví dụ 2, 3, 17 và False cho hợp số ví dụ 4, 9, 21.",
            "Code chạy được không có lỗi runtime và có ví dụ chạy thử ngắn.",
        ],
        "constraints": [
            "Keep the solution simple for Sprint 4.",
            "Write output in Vietnamese unless the task requires another language.",
        ],
        "context_files": ["docs/architecture/openclaw_knowledge_base_v2.txt"],
        "worker": "claude-cli",
        "priority": "high",
        "timeout_minutes": 30,
        "depends_on": [],
        "batch_id": batch_id,
    }

def build_prime_test_task(task_id: str, batch_id: str, dependency_ids: list[str]) -> dict[str, object]:
    return {
        "task_id": task_id,
        "project": "openclaw-ai",
        "goal": "Viết unit test cho hàm is_prime(n) kiểm tra số nguyên tố.",
        "acceptance_criteria": [
            "Unit test kiểm tra is_prime(n) trả về False cho n < 2, gồm n=0, n=1 và số âm.",
            "Unit test kiểm tra is_prime(n) trả về True cho số nguyên tố 2, 3, 17 và False cho hợp số 4, 9, 21.",
            "Test suite chạy được bằng Python standard library unittest hoặc pytest-style assertions.",
        ],
        "constraints": [
            "Keep the solution simple for Sprint 4.",
            "Use Python standard library unittest or pytest-style assertions.",
            "Write output in Vietnamese unless the task requires another language.",
        ],
        "context_files": [f"tasks/{dep}.json" for dep in dependency_ids],
        "worker": "claude-cli",
        "priority": "high",
        "timeout_minutes": 30,
        "depends_on": dependency_ids,
        "batch_id": batch_id,
    }

def build_batch_tasks(request: str) -> tuple[str, list[dict[str, object]]]:
    text = request.lower()

    if "số nguyên tố" in text or "so nguyen to" in text or "prime" in text or "is_prime" in text:
        wants_tests = "unit test" in text or "test" in text
        task_count = 1 + (1 if wants_tests else 0)
        task_ids = next_task_ids(task_count)
        batch_id = next_batch_id()
        tasks: list[dict[str, object]] = [build_prime_task(task_ids[0], batch_id)]
        if wants_tests:
            dependency_ids = [str(task["task_id"]) for task in tasks]
            tasks.append(build_prime_test_task(task_ids[-1], batch_id, dependency_ids))
        return batch_id, tasks

    temperature_keys: list[str] = []
    if "celsius_to_fahrenheit" in text or "c sang f" in text or "c to f" in text:
        temperature_keys.append("c_to_f")
    if "fahrenheit_to_celsius" in text or "f sang c" in text or "f to c" in text:
        temperature_keys.append("f_to_c")
    if "celsius_to_kelvin" in text or "c sang k" in text or "c to k" in text:
        temperature_keys.append("c_to_k")
    if temperature_keys:
        wants_tests = "unit test" in text or "test" in text
        task_count = len(temperature_keys) + (1 if wants_tests else 0)
        task_ids = next_task_ids(task_count)
        batch_id = next_batch_id()
        tasks: list[dict[str, object]] = []
        for task_id, function_key in zip(task_ids, temperature_keys):
            tasks.append(build_temperature_task(task_id, batch_id, function_key))
        if wants_tests:
            dependency_ids = [str(task["task_id"]) for task in tasks]
            tasks.append(build_temperature_test_task(task_ids[-1], batch_id, dependency_ids))
        return batch_id, tasks

    function_keys: list[str] = []
    if "trung bình" in text or "trung binh" in text:
        function_keys.append("mean")
    if "trung vị" in text or "trung vi" in text:
        function_keys.append("median")
    if "độ lệch chuẩn" in text or "do lech chuan" in text or "lech chuan" in text:
        function_keys.append("stddev")

    if not function_keys:
        raise ValueError("Không nhận diện được chức năng để chia batch")

    wants_tests = "unit test" in text or "test" in text
    task_count = len(function_keys) + (1 if wants_tests else 0)
    task_ids = next_task_ids(task_count)
    batch_id = next_batch_id()

    tasks: list[dict[str, object]] = []
    for task_id, function_key in zip(task_ids, function_keys):
        tasks.append(build_function_task(task_id, batch_id, function_key))

    if wants_tests:
        dependency_ids = [str(task["task_id"]) for task in tasks]
        tasks.append(build_test_task(task_ids[-1], batch_id, dependency_ids))

    return batch_id, tasks


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
    depends_on = task.get("depends_on", [])
    batch_id = task.get("batch_id", "N/A")
    content = f"""# {task_id} — Task created

## Metadata

- Created at: {now}
- Project: {task['project']}
- Worker: {task['worker']}
- Priority: {task['priority']}
- Timeout: {task['timeout_minutes']} minutes
- Depends on: {', '.join(depends_on) if depends_on else 'none'}
- Batch ID: {batch_id}
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


def write_and_validate_task(task: dict[str, object], request: str) -> Path:
    task_id = str(task["task_id"])
    task_path = TASKS_DIR / f"{task_id}.json"
    task_path.write_text(json.dumps(task, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    validate_task(task_path)
    write_task_log(task, request, task_path)
    return task_path


def print_batch_summary(batch_id: str, tasks: list[dict[str, object]]) -> None:
    print(f"✅ Batch {batch_id}: {len(tasks)} tasks created")
    for task in tasks:
        deps = task.get("depends_on", [])
        dep_text = "no deps" if not deps else "deps: " + ", ".join(str(dep) for dep in deps)
        print(f"   {task['task_id']} ({dep_text}) → {task['worker']}")


def main() -> int:
    args = parse_args()
    try:
        request = read_request(args)
        if args.batch:
            batch_id, tasks = build_batch_tasks(request)
            for task in tasks:
                write_and_validate_task(task, request)
            print_batch_summary(batch_id, tasks)
            return 0
    except ValueError as exc:
        print(f"❌ Lỗi: {exc}")
        return 1

    task_id = next_task_id()
    task = build_task(task_id, request)
    task_path = write_and_validate_task(task, request)

    print(f"✅ Task {task_id} đã tạo: {task_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
