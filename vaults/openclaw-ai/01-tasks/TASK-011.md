# TASK-011 — Task created

## Metadata

- Created at: 2026-06-06T20:47:34Z
- Project: openclaw-ai
- Worker: claude-cli
- Priority: high
- Timeout: 30 minutes
- Depends on: TASK-010
- Batch ID: B-003
- Task file: `tasks/TASK-011.json`

## User request

Viết hàm Python kiểm tra số nguyên tố.
Có unit test.

## Goal

Viết unit test cho hàm is_prime(n) kiểm tra số nguyên tố.

## Acceptance criteria

- Unit test kiểm tra is_prime(n) trả về False cho n < 2, gồm n=0, n=1 và số âm.
- Unit test kiểm tra is_prime(n) trả về True cho số nguyên tố 2, 3, 17 và False cho hợp số 4, 9, 21.
- Test suite chạy được bằng Python standard library unittest hoặc pytest-style assertions.

## Constraints

- Keep the solution simple for Sprint 4.
- Use Python standard library unittest or pytest-style assertions.
- Write output in Vietnamese unless the task requires another language.
