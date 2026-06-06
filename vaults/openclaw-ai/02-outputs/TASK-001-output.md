# TASK-001 - Hàm Python tính Fibonacci

## Code

```python
def fibonacci(n):
    if n < 0:
        raise ValueError("n phải là số nguyên không âm")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
```

## Ví dụ chạy thử

```python
print(fibonacci(0))   # 0
print(fibonacci(1))   # 1
print(fibonacci(5))   # 5
print(fibonacci(10))  # 55
```

Kết quả:

```text
0
1
5
55
```

## Cách hoạt động

Hàm bắt đầu với hai số đầu tiên của dãy Fibonacci là `0` và `1`. Mỗi vòng lặp cập nhật hai giá trị này thành số hiện tại và số tiếp theo. Sau `n` vòng lặp, biến `a` là số Fibonacci thứ `n`.

## Kiểm chứng

Đã kiểm tra các trường hợp:

- `fibonacci(0) == 0`
- `fibonacci(1) == 1`
- `fibonacci(5) == 5`
- `fibonacci(10) == 55`

Code chạy không có lỗi runtime.
