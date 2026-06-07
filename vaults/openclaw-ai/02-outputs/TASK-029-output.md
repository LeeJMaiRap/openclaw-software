# TASK-029 — Phạm vi hàm giai thừa đệ quy

## Đặc tả

- Hàm nhận đầu vào là một số nguyên không âm `n`.
- Hàm trả về giá trị giai thừa `n!`.
- Hàm phải dùng đệ quy, không dùng vòng lặp.
- Công thức:
  - `0! = 1`
  - `1! = 1`
  - `n! = n * (n - 1)!` với `n > 1`

## Trường hợp cơ bản

Nêu rõ kết quả đúng cho các trường hợp cơ bản như `0!` và `1!`:

- `0! = 1`, nên `factorial(0)` trả về `1`.
- `1! = 1`, nên `factorial(1)` trả về `1`.
- `5! = 120`, nên `factorial(5)` trả về `120`.

## Ghi chú kiểm thử

Unit test cần bao phủ ít nhất `0`, `1`, `5` và lỗi đầu vào âm.
