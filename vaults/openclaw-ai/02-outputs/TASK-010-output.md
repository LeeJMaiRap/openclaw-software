# TASK-010 - Hàm `is_prime(n)`

## Mục tiêu
Viết hàm Python `is_prime(n)` để kiểm tra một số nguyên có phải số nguyên tố hay không.

## Code
```python
def is_prime(n):
    if n < 2:
        return False

    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False

    return True


# Ví dụ chạy thử ngắn
if __name__ == "__main__":
    test_numbers = [-5, 0, 1, 2, 3, 4, 9, 17, 21]
    for number in test_numbers:
        print(f"{number}: {is_prime(number)}")
```

## Kết quả mong đợi
```text
-5: False
0: False
1: False
2: True
3: True
4: False
9: False
17: True
21: False
```

## Ghi chú xác minh
- `n < 2` trả về `False`, gồm số âm, `0`, `1`.
- `2`, `3`, `17` trả về `True`.
- `4`, `9`, `21` trả về `False`.
- Code đơn giản, chạy được trong Python không cần thư viện ngoài.
