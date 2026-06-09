# TASK-036 — Task created

## Metadata

- Created at: 2026-06-09T11:58:45Z
- Project: openclaw-ai
- Worker: claude-cli
- Priority: high
- Timeout: 30 minutes
- Depends on: TASK-035
- Batch ID: B-011
- Task file: `tasks/TASK-036.json`

## User request

Viết hàm Python đếm số nguyên tố trong khoảng [a, b]. Có unit test.

## Goal

Tạo hàm Python hoạt động đúng để đếm số nguyên tố trong khoảng [a, b] theo đặc tả đã phân tích.

## Acceptance criteria

- Có hàm Python nhận 2 tham số nguyên a, b và trả về một số nguyên là lượng số nguyên tố trong [a, b]
- Kết quả đúng với các trường hợp cơ bản như [2,2], [1,10], [10,20] và trường hợp không có số nguyên tố
- Mã chạy được không lỗi cú pháp và không dùng thư viện ngoài không cần thiết

## Constraints

- Keep the solution simple for Sprint 5.
- Write output in Vietnamese unless the task requires another language.
