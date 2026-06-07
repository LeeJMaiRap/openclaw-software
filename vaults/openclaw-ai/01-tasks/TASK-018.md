# TASK-018 — Task created

## Metadata

- Created at: 2026-06-07T04:48:35Z
- Project: openclaw-ai
- Worker: claude-cli
- Priority: high
- Timeout: 30 minutes
- Depends on: TASK-015, TASK-016
- Batch ID: B-005
- Task file: `tasks/TASK-018.json`

## User request

So sánh bubble sort và quick sort: viết cả 2, benchmark, có unit test

## Goal

Tạo mã benchmark chạy bubble sort và quick sort trên cùng bộ dữ liệu, ghi nhận thời gian chạy và xuất kết quả so sánh

## Acceptance criteria

- Benchmark chạy được cho cả 2 thuật toán trên cùng tập dữ liệu đầu vào
- Kết quả benchmark hiển thị hoặc ghi ra thời gian chạy theo từng kích thước dữ liệu
- Benchmark có bước kiểm tra kết quả sắp xếp hợp lệ trước khi ghi nhận kết quả

## Constraints

- Keep the solution simple for Sprint 5.
- Write output in Vietnamese unless the task requires another language.
