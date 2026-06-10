# TASK-040 - Unit test cho hàm chuyển số La Mã

## Kết quả

Đã tạo file unit test riêng:

- `/data/workspace/openclaw-ai/tests/test_roman_numerals.py`

File test tách khỏi file code hàm:

- Code hàm: `/data/workspace/openclaw-ai/roman_numerals.py`
- Unit test: `/data/workspace/openclaw-ai/tests/test_roman_numerals.py`

## Nội dung test

Bộ test dùng `unittest` và kiểm tra hàm `roman_to_int`.

Các nhóm test:

1. Ca cơ bản:
   - `I -> 1`
   - `III -> 3`
   - `V -> 5`

2. Ca có quy tắc trừ:
   - `IV -> 4`
   - `IX -> 9`
   - `XL -> 40`
   - `CM -> 900`

3. Ca tổng hợp dài:
   - `MCMXCIV -> 1994`

## Ghi chú kiểm chứng

Đã chạy lệnh:

```bash
python3 -m unittest /data/workspace/openclaw-ai/tests/test_roman_numerals.py
```

Kết quả:

```text
Ran 3 tests in 0.000s

OK
```
