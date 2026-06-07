# TASK-028 — Task created

## Metadata

- Created at: 2026-06-07T07:52:01Z
- Project: openclaw-ai
- Worker: claude-cli
- Priority: high
- Timeout: 30 minutes
- Depends on: TASK-027
- Batch ID: B-008
- Task file: `tasks/TASK-028.json`

## User request

Xây dựng REST API đơn giản bằng Python dùng http.server. Có unit test.

## Goal

Tạo bộ unit test riêng để kiểm tra hành vi chính của REST API, gồm ca thành công và ca lỗi.

## Acceptance criteria

- Unit test là task riêng và nằm trong file test tách biệt mã nguồn chính
- Có test cho ít nhất 1 ca thành công và 1 ca lỗi của API
- Test xác minh mã trạng thái HTTP và nội dung JSON response
- Toàn bộ test chạy pass bằng công cụ test chuẩn của Python

## Constraints

- Keep the solution simple for Sprint 5.
- Write output in Vietnamese unless the task requires another language.
