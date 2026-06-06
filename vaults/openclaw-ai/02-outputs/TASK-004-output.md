# TASK-004 - Hàm tính độ lệch chuẩn Python

## Code

```python
import math


def tinh_do_lech_chuan(data):
    """Tính độ lệch chuẩn population (chia cho n) cho danh sách số."""
    if not data:
        raise ValueError("data không được rỗng")

    trung_binh = sum(data) / len(data)
    phuong_sai = sum((x - trung_binh) ** 2 for x in data) / len(data)
    return math.sqrt(phuong_sai)


if __name__ == "__main__":
    vi_du_1 = [2, 4, 4, 4, 5, 5, 7, 9]
    vi_du_2 = [1, 2, 3, 4, 5]

    print("Ví dụ 1:", tinh_do_lech_chuan(vi_du_1))  # kỳ vọng: 2.0
    print("Ví dụ 2:", tinh_do_lech_chuan(vi_du_2))  # kỳ vọng: sqrt(2) ≈ 1.4142135624
```

## Ghi chú

- Hàm này tính **độ lệch chuẩn population**.
- Công thức dùng phương sai chia cho `n`, không chia cho `n - 1`.
- Nếu `data` rỗng, hàm báo lỗi `ValueError`.

## Kết quả ví dụ

- `[2, 4, 4, 4, 5, 5, 7, 9]` → `2.0`
- `[1, 2, 3, 4, 5]` → `1.4142135623730951`

## Verification notes

- Đã chạy thử bằng `python3 /tmp/task004_verify.py`.
- Có 2 kiểm tra `assert` với `math.isclose`.
- Code chạy không lỗi runtime bằng Python 3.
