# TASK-010 — Task created

## Metadata

- Created at: 2026-06-06T20:47:34Z
- Project: openclaw-ai
- Worker: claude-cli
- Priority: high
- Timeout: 30 minutes
- Depends on: none
- Batch ID: B-003
- Task file: `tasks/TASK-010.json`

## User request

Viết hàm Python kiểm tra số nguyên tố.
Có unit test.

## Goal

Viết hàm Python is_prime(n) để kiểm tra một số nguyên có phải số nguyên tố hay không.

## Acceptance criteria

- Hàm is_prime(n) trả về False cho n < 2, gồm n=0, n=1 và số âm.
- Hàm is_prime(n) trả về True cho các số nguyên tố ví dụ 2, 3, 17 và False cho hợp số ví dụ 4, 9, 21.
- Code chạy được không có lỗi runtime và có ví dụ chạy thử ngắn.

## Constraints

- Keep the solution simple for Sprint 4.
- Write output in Vietnamese unless the task requires another language.
