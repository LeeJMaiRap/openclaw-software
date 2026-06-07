# TASK-030 — Hàm Python `factorial`

## Kết quả

Đã tạo file:

```text
/data/workspace/openclaw-ai/factorial.py
```

## Code chính

```python
def factorial(n: int) -> int:
    """Return n! for a non-negative integer n using recursion."""
    if n < 0:
        raise ValueError("factorial is only defined for non-negative integers")
    if n in (0, 1):
        return 1
    return n * factorial(n - 1)
```

## Acceptance criteria

- Có hàm Python tên `factorial`.
- Hàm dùng lời gọi đệ quy `factorial(n - 1)` để tính `n!`.
- `factorial(0)` trả về `1` và `factorial(1)` trả về `1`.
- `factorial(5)` trả về `120`.

## Verification

```text
python3 -m py_compile factorial.py
```

Pass, không có lỗi cú pháp.
