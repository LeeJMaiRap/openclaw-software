# TASK-009 — Task created

## Metadata

- Created at: 2026-06-06T13:42:55Z
- Project: openclaw-ai
- Worker: claude-cli
- Priority: high
- Timeout: 30 minutes
- Depends on: TASK-006, TASK-007, TASK-008
- Batch ID: B-002
- Task file: `tasks/TASK-009.json`

## User request

Xây dựng module đổi nhiệt độ:
hàm celsius_to_fahrenheit, fahrenheit_to_celsius,
celsius_to_kelvin. Có unit test.

## Goal

Viết unit test cho các hàm đổi nhiệt độ: celsius_to_fahrenheit, fahrenheit_to_celsius, celsius_to_kelvin.

## Acceptance criteria

- Unit test kiểm tra celsius_to_fahrenheit(c) với c=0, c=100 và c=-40.
- Unit test kiểm tra fahrenheit_to_celsius(f) với f=32, f=212 và f=-40.
- Unit test kiểm tra celsius_to_kelvin(c) với c=0, c=100 và c=-273.15 và test suite chạy được.

## Constraints

- Keep the solution simple for Sprint 3.
- Use Python standard library unittest or pytest-style assertions.
- Write output in Vietnamese unless the task requires another language.
