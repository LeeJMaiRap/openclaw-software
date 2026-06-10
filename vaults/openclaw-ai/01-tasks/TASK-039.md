# TASK-039 — Task created

## Metadata

- Created at: 2026-06-10T06:33:57Z
- Project: openclaw-ai
- Worker: claude-cli
- Priority: high
- Timeout: 30 minutes
- Depends on: TASK-038
- Batch ID: B-012
- Task file: `tasks/TASK-039.json`

## User request

Viết hàm Python chuyển đổi số La Mã sang số nguyên. Có unit test.

## Goal

Tạo hàm Python nhận chuỗi số La Mã và trả về đúng số nguyên theo quy tắc đã phân tích.

## Acceptance criteria

- Có hàm Python tên phù hợp, nhận 1 chuỗi đầu vào và trả về 1 số nguyên
- Xử lý đúng các cặp trừ chuẩn: IV, IX, XL, XC, CD, CM
- Kết quả đúng với ví dụ phổ biến như III -> 3, LVIII -> 58, MCMXCIV -> 1994

## Constraints

- Keep the solution simple for Sprint 5.
- Write output in Vietnamese unless the task requires another language.
