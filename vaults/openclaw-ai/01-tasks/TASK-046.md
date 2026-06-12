# TASK-046 — Task created

## Metadata

- Created at: 2026-06-11T13:20:24Z
- Project: openclaw-ai
- Worker: claude-cli
- Priority: high
- Timeout: 20 minutes
- Depends on: TASK-045
- Batch ID: B-014
- Task file: `tasks/TASK-046.json`

## User request

Viết hàm Python đếm số nguyên tố trong list. Có unit test.

## Goal

Tạo bộ unit test kiểm tra đầy đủ hành vi chính của hàm đếm số nguyên tố

## Acceptance criteria

- Có test cho list rỗng và trả về 0
- Có test cho list chứa số âm, 0, 1 để xác nhận không bị tính là số nguyên tố
- Có test cho list chứa nhiều số nguyên tố và hợp số với kết quả đếm chính xác
- Toàn bộ unit test chạy pass với implementation đã viết

## Constraints

- Keep the solution simple for Sprint 5.
- Write output in Vietnamese unless the task requires another language.
