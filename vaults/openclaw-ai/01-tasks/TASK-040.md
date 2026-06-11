# TASK-040 — Task created

## Metadata

- Created at: 2026-06-10T06:33:57Z
- Project: openclaw-ai
- Worker: claude-cli
- Priority: high
- Timeout: 30 minutes
- Depends on: TASK-039
- Batch ID: B-012
- Task file: `tasks/TASK-040.json`

## User request

Viết hàm Python chuyển đổi số La Mã sang số nguyên. Có unit test.

## Goal

Tạo bộ unit test riêng để kiểm tra các ca cơ bản, ca có quy tắc trừ, và ca tổng hợp cho hàm chuyển đổi số La Mã.

## Acceptance criteria

- Unit test là file riêng, tách khỏi file code hàm
- Có test cho ca cơ bản như I, III, V
- Có test cho các ca trừ như IV, IX, XL, CM
- Có test cho ít nhất 1 ca tổng hợp dài như MCMXCIV

## Constraints

- Keep the solution simple for Sprint 5.
- Write output in Vietnamese unless the task requires another language.
