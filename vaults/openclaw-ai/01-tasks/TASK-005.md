# TASK-005 — Task created

## Metadata

- Created at: 2026-06-06T09:19:55Z
- Project: openclaw-ai
- Worker: claude-cli
- Priority: high
- Timeout: 30 minutes
- Depends on: TASK-002, TASK-003, TASK-004
- Batch ID: B-001
- Task file: `tasks/TASK-005.json`

## User request

Xây dựng một module Python tính toán thống kê cơ bản: trung bình, trung vị, độ lệch chuẩn. Có unit test.

## Goal

Viết unit test cho các hàm thống kê cơ bản: tinh_trung_binh, tinh_trung_vi, tinh_do_lech_chuan.

## Acceptance criteria

- Unit test kiểm tra tinh_trung_binh(data) với ít nhất 2 bộ dữ liệu.
- Unit test kiểm tra tinh_trung_vi(data) với danh sách có số phần tử chẵn và lẻ.
- Unit test kiểm tra tinh_do_lech_chuan(data) với ít nhất 2 bộ dữ liệu và test suite chạy được.

## Constraints

- Keep the solution simple for Sprint 2.
- Use Python standard library unittest or pytest-style assertions.
- Write output in Vietnamese unless the task requires another language.
