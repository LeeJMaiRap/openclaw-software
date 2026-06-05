#!/usr/bin/env python3
"""Validate an OpenClaw AI task file.

Usage:
    python3 validators/validate_task.py <file>
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "task.schema.json"


class ValidationError(Exception):
    pass


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise ValidationError(f"Không tìm thấy file: {path}")
    except json.JSONDecodeError as exc:
        raise ValidationError(f"JSON không hợp lệ tại dòng {exc.lineno}, cột {exc.colno}: {exc.msg}")


def field_name(path: str, name: str) -> str:
    if not path:
        return name
    return f"{path}.{name}"


def validate_value(value: Any, schema: dict[str, Any], path: str = "") -> None:
    if "type" in schema:
        expected_type = schema["type"]
        if expected_type == "object" and not isinstance(value, dict):
            raise ValidationError(f"{path or 'root'} phải là object")
        if expected_type == "array" and not isinstance(value, list):
            raise ValidationError(f"{path} phải là array")
        if expected_type == "string" and not isinstance(value, str):
            raise ValidationError(f"{path} phải là string")
        if expected_type == "integer" and (not isinstance(value, int) or isinstance(value, bool)):
            raise ValidationError(f"{path} phải là integer")

    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                raise ValidationError(f"Thiếu field bắt buộc: {field_name(path, key)}")

        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            allowed = set(properties.keys())
            extra = sorted(set(value.keys()) - allowed)
            if extra:
                raise ValidationError(f"Field không được phép: {field_name(path, extra[0])}")

        for key, child_value in value.items():
            if key in properties:
                validate_value(child_value, properties[key], field_name(path, key))
        return

    if isinstance(value, list):
        min_items = schema.get("minItems")
        if min_items is not None and len(value) < min_items:
            raise ValidationError(f"{path} phải có ít nhất {min_items} phần tử")

        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(value):
                validate_value(item, item_schema, f"{path}[{index}]")
        return

    if isinstance(value, str):
        min_length = schema.get("minLength")
        if min_length is not None and len(value) < min_length:
            raise ValidationError(f"{path} phải dài ít nhất {min_length} ký tự")

        pattern = schema.get("pattern")
        if pattern and re.fullmatch(pattern, value) is None:
            raise ValidationError(f"{path} không khớp pattern {pattern}")

        enum = schema.get("enum")
        if enum is not None and value not in enum:
            allowed = ", ".join(enum)
            raise ValidationError(f"{path} phải là một trong: {allowed}")
        return

    if isinstance(value, int) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        if minimum is not None and value < minimum:
            raise ValidationError(f"{path} phải >= {minimum}")

        maximum = schema.get("maximum")
        if maximum is not None and value > maximum:
            raise ValidationError(f"{path} phải <= {maximum}")
        return


def main() -> int:
    if len(sys.argv) != 2:
        print("❌ Lỗi: Cách dùng: python3 validators/validate_task.py <file>")
        return 2

    task_path = Path(sys.argv[1])

    try:
        schema = load_json(SCHEMA_PATH)
        task = load_json(task_path)
        validate_value(task, schema)
    except ValidationError as exc:
        print(f"❌ Lỗi: {exc}")
        return 1

    print("✅ Task file hợp lệ")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
