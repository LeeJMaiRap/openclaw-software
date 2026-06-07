# TASK-014 — Task created

## Metadata

- Created at: 2026-06-07T04:13:31Z
- Project: openclaw-ai
- Worker: claude-cli
- Priority: medium
- Timeout: 30 minutes
- Depends on: TASK-013
- Batch ID: B-004
- Task file: `tasks/TASK-014.json`

## User request

Viết script Python
 đọc file CSV và tính tổng theo từng cột số

## Goal

Tạo bộ unit test kiểm tra hành vi chính của script với dữ liệu CSV mẫu cho cột số và cột không phải số.

## Acceptance criteria

- Có test cho trường hợp CSV gồm nhiều cột số và kết quả tổng đúng từng cột.
- Có test cho trường hợp CSV có cột chữ và cột đó bị bỏ qua.
- Tất cả test chạy pass bằng framework test Python được chọn.

## Constraints

- Keep the solution simple for Sprint 5.
- Write output in Vietnamese unless the task requires another language.
