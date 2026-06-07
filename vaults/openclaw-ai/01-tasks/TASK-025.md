# TASK-025 — Task created

## Metadata

- Created at: 2026-06-07T06:03:59Z
- Project: openclaw-ai
- Worker: claude-cli
- Priority: high
- Timeout: 20 minutes
- Depends on: TASK-024
- Batch ID: B-007
- Task file: `tasks/TASK-025.json`

## User request

Viết hàm Python đảo ngược chuỗi. Có unit test.

## Goal

Tạo bộ unit test kiểm tra tính đúng đắn của hàm đảo ngược chuỗi với các trường hợp phổ biến và biên

## Acceptance criteria

- Có test cho ít nhất 4 trường hợp: chuỗi thường, chuỗi rỗng, 1 ký tự, chuỗi có khoảng trắng hoặc ký tự đặc biệt
- Tất cả test pass khi chạy với hàm đã viết
- Test độc lập và có thể chạy bằng framework test Python phổ biến

## Constraints

- Keep the solution simple for Sprint 5.
- Write output in Vietnamese unless the task requires another language.
