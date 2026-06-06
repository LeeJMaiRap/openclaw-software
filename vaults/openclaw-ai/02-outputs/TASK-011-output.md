# TASK-011 - Unit test cho `is_prime(n)`

## Mục tiêu
Viết unit test cho hàm `is_prime(n)` kiểm tra số nguyên tố.

## File đã tạo
- `/data/workspace/openclaw-ai/prime.py`
- `/data/workspace/openclaw-ai/tests/test_prime.py`

## Nội dung test
```python
import unittest

from prime import is_prime


class TestIsPrime(unittest.TestCase):
    def test_numbers_less_than_two_are_not_prime(self):
        self.assertFalse(is_prime(-5))
        self.assertFalse(is_prime(0))
        self.assertFalse(is_prime(1))

    def test_prime_numbers(self):
        self.assertTrue(is_prime(2))
        self.assertTrue(is_prime(3))
        self.assertTrue(is_prime(17))

    def test_composite_numbers(self):
        self.assertFalse(is_prime(4))
        self.assertFalse(is_prime(9))
        self.assertFalse(is_prime(21))


if __name__ == "__main__":
    unittest.main()
```

## Ghi chú xác minh
- Test kiểm tra `False` cho `n < 2`: `-5`, `0`, `1`.
- Test kiểm tra số nguyên tố `2`, `3`, `17` trả về `True`.
- Test kiểm tra hợp số `4`, `9`, `21` trả về `False`.
- Test dùng Python standard library `unittest`, không cần thư viện ngoài.

## Lệnh xác minh
```bash
python3 -m unittest tests/test_prime.py
```

## Kết quả
```text
...
----------------------------------------------------------------------
Ran 3 tests in 0.000s

OK
```
