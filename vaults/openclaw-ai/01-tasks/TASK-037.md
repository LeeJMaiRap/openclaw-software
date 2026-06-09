# TASK-037 — Task created

## Metadata

- Created at: 2026-06-09T11:58:45Z
- Project: openclaw-ai
- Worker: claude-cli
- Priority: high
- Timeout: 30 minutes
- Depends on: TASK-036
- Batch ID: B-011
- Task file: `tasks/TASK-037.json`

## User request

Viết hàm Python đếm số nguyên tố trong khoảng [a, b]. Có unit test.

## Goal

Tạo bộ unit test riêng để kiểm tra tính đúng đắn của hàm trên các trường hợp chuẩn và biên.

## Acceptance criteria

- Có file unit test riêng phụ thuộc vào hàm đã viết
- Bao phủ ít nhất các ca: khoảng chỉ có 1 số nguyên tố, khoảng nhiều số nguyên tố, khoảng không có số nguyên tố, và biên với giá trị nhỏ hơn 2
- Chạy test cho kết quả pass toàn bộ với implementation đúng

## Constraints

- Keep the solution simple for Sprint 5.
- Write output in Vietnamese unless the task requires another language.
