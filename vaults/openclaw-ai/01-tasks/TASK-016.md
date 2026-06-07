# TASK-016 — Task created

## Metadata

- Created at: 2026-06-07T04:48:35Z
- Project: openclaw-ai
- Worker: claude-cli
- Priority: high
- Timeout: 30 minutes
- Depends on: TASK-015
- Batch ID: B-005
- Task file: `tasks/TASK-016.json`

## User request

So sánh bubble sort và quick sort: viết cả 2, benchmark, có unit test

## Goal

Viết mã nguồn cho 2 hàm sắp xếp bubble sort và quick sort, cùng giao diện gọi thống nhất để dùng cho test và benchmark

## Acceptance criteria

- Có 2 hàm riêng cho bubble sort và quick sort
- Cả 2 hàm trả về kết quả sắp xếp tăng dần đúng với dữ liệu số nguyên đầu vào
- Mã nguồn có thể được import hoặc gọi lại từ module test và benchmark

## Constraints

- Keep the solution simple for Sprint 5.
- Write output in Vietnamese unless the task requires another language.
