# TASK-009 — Unit test cho hàm đổi nhiệt độ

## Tệp đã tạo

- `temperature_conversions.py`
- `tests/test_temperature_conversions.py`

## Nội dung kiểm thử

Test suite dùng Python standard library `unittest`.

Các ca kiểm thử đã có:

1. `celsius_to_fahrenheit(c)`
   - `c=0` → `32`
   - `c=100` → `212`
   - `c=-40` → `-40`

2. `fahrenheit_to_celsius(f)`
   - `f=32` → `0`
   - `f=212` → `100`
   - `f=-40` → `-40`

3. `celsius_to_kelvin(c)`
   - `c=0` → `273.15`
   - `c=100` → `373.15`
   - `c=-273.15` → `0`

## Cách chạy

```bash
python3 -m unittest discover -s tests -v
```

## Ghi chú kiểm chứng

Đã chạy lệnh:

```bash
python3 -m unittest discover -s tests -v
```

Kết quả:

```text
Ran 3 tests in 0.000s

OK
```

Ghi chú nhỏ: lệnh `python` không có trong môi trường này, nên dùng `python3` để chạy test.
