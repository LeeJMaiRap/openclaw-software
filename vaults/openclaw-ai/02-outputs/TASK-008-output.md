# TASK-008: Hàm đổi Celsius sang Kelvin

## Code Python

```python
def celsius_to_kelvin(c):
    return c + 273.15
```

## Ví dụ chạy thử

```python
print(celsius_to_kelvin(0))       # 273.15
print(celsius_to_kelvin(100))     # 373.15
print(celsius_to_kelvin(-273.15)) # 0.0
```

Kết quả:

```text
0°C -> 273.15 K
100°C -> 373.15 K
-273.15°C -> 0.0 K
```

## Giải thích ngắn

Công thức chuyển đổi từ Celsius sang Kelvin là:

```text
K = °C + 273.15
```

Vì vậy hàm chỉ cần cộng giá trị Celsius với `273.15`.

## Ghi chú kiểm chứng

- `celsius_to_kelvin(0)` trả về `273.15`.
- `celsius_to_kelvin(100)` trả về `373.15`.
- `celsius_to_kelvin(-273.15)` trả về `0.0`.
- Code đã chạy bằng Python không có lỗi runtime.
