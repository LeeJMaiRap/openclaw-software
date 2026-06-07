#!/usr/bin/env python3
"""Tính tổng các cột số trong file CSV."""

import argparse
import csv
from decimal import Decimal, InvalidOperation


def read_csv_totals(path):
    """Trả về dict {tên_cột: tổng} cho các cột có toàn bộ giá trị không rỗng là số."""
    with open(path, newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        if not reader.fieldnames:
            return {}

        totals = {name: Decimal("0") for name in reader.fieldnames}
        is_numeric = {name: True for name in reader.fieldnames}

        for row in reader:
            for name in reader.fieldnames:
                value = (row.get(name) or "").strip()
                if value == "":
                    continue
                try:
                    totals[name] += Decimal(value)
                except InvalidOperation:
                    is_numeric[name] = False

        return {name: totals[name] for name in reader.fieldnames if is_numeric[name]}


def format_number(value):
    """In số gọn: bỏ .0 dư nếu có."""
    normalized = value.normalize()
    if normalized == normalized.to_integral():
        return str(normalized.quantize(Decimal("1")))
    return format(normalized, "f")


def main():
    parser = argparse.ArgumentParser(description="Tính tổng từng cột số trong file CSV.")
    parser.add_argument("csv_path", help="Đường dẫn tới file CSV")
    args = parser.parse_args()

    totals = read_csv_totals(args.csv_path)
    if not totals:
        print("Không tìm thấy cột số.")
        return

    for name, total in totals.items():
        print(f"{name}: {format_number(total)}")


if __name__ == "__main__":
    main()
