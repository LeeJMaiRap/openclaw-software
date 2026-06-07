# TASK-017 — Task created

## Metadata

- Created at: 2026-06-07T04:48:35Z
- Project: openclaw-ai
- Worker: claude-cli
- Priority: high
- Timeout: 30 minutes
- Depends on: TASK-016
- Batch ID: B-005
- Task file: `tasks/TASK-017.json`

## User request

So sánh bubble sort và quick sort: viết cả 2, benchmark, có unit test

## Goal

Tạo bộ unit test riêng kiểm tra tính đúng đắn của bubble sort và quick sort trên các trường hợp điển hình và biên

## Acceptance criteria

- Có test cho mảng rỗng, 1 phần tử, đã sắp xếp, đảo ngược và có phần tử trùng lặp
- Cả bubble sort và quick sort đều vượt qua toàn bộ test
- Test được tách thành task riêng và chỉ phụ thuộc task cài đặt mã nguồn

## Constraints

- Keep the solution simple for Sprint 5.
- Write output in Vietnamese unless the task requires another language.
