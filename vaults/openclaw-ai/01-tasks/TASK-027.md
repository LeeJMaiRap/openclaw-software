# TASK-027 — Task created

## Metadata

- Created at: 2026-06-07T07:52:01Z
- Project: openclaw-ai
- Worker: claude-cli
- Priority: high
- Timeout: 30 minutes
- Depends on: TASK-026
- Batch ID: B-008
- Task file: `tasks/TASK-027.json`

## User request

Xây dựng REST API đơn giản bằng Python dùng http.server. Có unit test.

## Goal

Tạo ứng dụng Python chạy được bằng http.server, cung cấp các endpoint REST đã phân tích, xử lý JSON request/response và trả về mã trạng thái HTTP đúng.

## Acceptance criteria

- Có file mã nguồn Python chạy được và khởi tạo HTTP server bằng http.server
- API xử lý thành công các phương thức và endpoint đã đặc tả
- Response trả về JSON hợp lệ và có Content-Type phù hợp
- Có xử lý trường hợp input không hợp lệ với mã lỗi HTTP phù hợp

## Constraints

- Keep the solution simple for Sprint 5.
- Write output in Vietnamese unless the task requires another language.
