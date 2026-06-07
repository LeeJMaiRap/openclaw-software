# TASK-022 — Task created

## Metadata

- Created at: 2026-06-07T04:57:26Z
- Project: openclaw-ai
- Worker: claude-cli
- Priority: high
- Timeout: 30 minutes
- Depends on: TASK-021
- Batch ID: B-006
- Task file: `tasks/TASK-022.json`

## User request

Xây dựng module quản lý todo list: thêm, xóa, đánh dấu hoàn thành, lưu vào file JSON. Có unit test.

## Goal

Tạo bộ unit test kiểm tra đầy đủ các chức năng chính của module todo và hành vi lưu/đọc JSON.

## Acceptance criteria

- Có test riêng cho thêm todo, xóa todo và đánh dấu hoàn thành
- Có test kiểm tra dữ liệu được lưu ra file JSON đúng cấu trúc mong đợi
- Có test kiểm tra đọc dữ liệu từ file JSON khôi phục đúng danh sách todo
- Toàn bộ unit test chạy pass

## Constraints

- Keep the solution simple for Sprint 5.
- Write output in Vietnamese unless the task requires another language.
