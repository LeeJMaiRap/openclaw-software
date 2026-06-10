# TASK-039 - Hàm chuyển số La Mã sang số nguyên

## Kết quả

Đã tạo file mã nguồn:

- `/data/workspace/openclaw-ai/roman_numerals.py`

Hàm chính:

```python
def roman_to_int(roman: str) -> int:
    """Convert a Roman numeral string to an integer."""
```

## Cách xử lý

- Dùng bảng giá trị cho 7 ký tự: `I`, `V`, `X`, `L`, `C`, `D`, `M`.
- Duyệt chuỗi từ trái sang phải.
- Nếu gặp cặp trừ chuẩn thì cộng giá trị cặp và nhảy 2 ký tự:
  - `IV`, `IX`, `XL`, `XC`, `CD`, `CM`
- Nếu không phải cặp trừ thì cộng giá trị ký tự hiện tại và nhảy 1 ký tự.
- Nếu chuỗi rỗng, ký tự không hợp lệ, hoặc cặp trừ không chuẩn như `IL`, hàm raise `ValueError`.

## Ví dụ đúng

- `roman_to_int("III")` trả về `3`
- `roman_to_int("LVIII")` trả về `58`
- `roman_to_int("MCMXCIV")` trả về `1994`

## Ghi chú kiểm chứng

Đã chạy kiểm chứng bằng `python3` với các trường hợp:

- `III -> 3`
- `IV -> 4`
- `IX -> 9`
- `LVIII -> 58`
- `XL -> 40`
- `XC -> 90`
- `CD -> 400`
- `CM -> 900`
- `MCMXCIV -> 1994`
- `IL` bị từ chối bằng `ValueError`

Kết quả: `roman_numerals verification passed`.
