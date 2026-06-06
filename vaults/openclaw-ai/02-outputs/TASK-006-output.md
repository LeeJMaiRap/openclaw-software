# TASK-006 - Chuyển Celsius sang Fahrenheit

## Code Python

```python
def celsius_to_fahrenheit(c):
    return c * 9 / 5 + 32
```

## Ví dụ chạy thử

```python
print(celsius_to_fahrenheit(0))     # 32.0
print(celsius_to_fahrenheit(100))   # 212.0
print(celsius_to_fahrenheit(-40))   # -40.0
```

## Giải thích ngắn

Công thức chuyển đổi từ Celsius sang Fahrenheit:

```text
F = C * 9 / 5 + 32
```

Trong đó `C` là nhiệt độ Celsius, `F` là nhiệt độ Fahrenheit.

## Ghi chú kiểm chứng

- `celsius_to_fahrenheit(0)` trả về `32`.
- `celsius_to_fahrenheit(100)` trả về `212`.
- `celsius_to_fahrenheit(-40)` trả về `-40`.
- Đã chạy kiểm thử Python, không có lỗi runtime.
