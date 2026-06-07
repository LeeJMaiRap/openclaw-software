# TASK-021 — Task created

## Metadata

- Created at: 2026-06-07T04:57:26Z
- Project: openclaw-ai
- Worker: claude-cli
- Priority: high
- Timeout: 30 minutes
- Depends on: TASK-020
- Batch ID: B-006
- Task file: `tasks/TASK-021.json`

## User request

Xây dựng module quản lý todo list: thêm, xóa, đánh dấu hoàn thành, lưu vào file JSON. Có unit test.

## Goal

Xây dựng module todo list hỗ trợ thêm, xóa, đánh dấu hoàn thành và lưu dữ liệu vào file JSON theo thiết kế đã thống nhất.

## Acceptance criteria

- Có thể thêm mới một todo và lưu trong danh sách ở bộ nhớ
- Có thể xóa todo theo id hoặc khóa định danh đã chọn trong thiết kế
- Có thể đánh dấu hoàn thành cho một todo đang tồn tại
- Có chức năng ghi danh sách todo ra file JSON và đọc lại đúng cấu trúc

## Constraints

- Keep the solution simple for Sprint 5.
- Write output in Vietnamese unless the task requires another language.
