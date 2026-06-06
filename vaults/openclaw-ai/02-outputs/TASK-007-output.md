# TASK-007 — Hàm đổi Fahrenheit sang Celsius

## Code Python

```python
def fahrenheit_to_celsius(f):
    return (f - 32) * 5 / 9
```

## Ví dụ chạy thử

```python
print(fahrenheit_to_celsius(32))    # 0.0
print(fahrenheit_to_celsius(212))   # 100.0
print(fahrenheit_to_celsius(-40))   # -40.0
```

## Công thức

Celsius = (Fahrenheit - 32) × 5 / 9

Nghĩa là lấy nhiệt độ Fahrenheit trừ 32, rồi nhân với 5/9 để ra Celsius.

## Kết quả kiểm tra

- `fahrenheit_to_celsius(32)` trả về `0.0`
- `fahrenheit_to_celsius(212)` trả về `100.0`
- `fahrenheit_to_celsius(-40)` trả về `-40.0`

Code chạy không có lỗi runtime.
