# TASK-045 Output

## Kết quả

Đã tạo hàm Python `count_primes(numbers)` trong file:

- `/data/workspace/openclaw-ai/prime.py`

Hàm nhận vào một list và trả về số nguyên là số lượng số nguyên tố trong list.

## Code chính

```python
def count_primes(numbers):
    """Đếm số lượng số nguyên tố trong list đầu vào."""
    return sum(1 for number in numbers if is_prime(number))
```

## Xử lý trường hợp

- Số âm: không tính là số nguyên tố
- `0`: không tính là số nguyên tố
- `1`: không tính là số nguyên tố
- Số nguyên tố: được tính
- Hợp số: không được tính
- List rỗng: trả về `0`

## Kiểm chứng

Đã thêm test trong:

- `/data/workspace/openclaw-ai/tests/test_prime.py`

Lệnh kiểm thử đã chạy:

```bash
python3 -m unittest /data/workspace/openclaw-ai/tests/test_prime.py
```

Kết quả:

```text
Ran 6 tests in 0.000s

OK
```

Ghi chú: lệnh `python` không tồn tại trong môi trường này, nên đã dùng `python3`.

## Xác nhận acceptance criteria

- Code chạy được, không lỗi cú pháp: đã kiểm chứng bằng `python3 -m unittest /data/workspace/openclaw-ai/tests/test_prime.py` và toàn bộ test pass.
