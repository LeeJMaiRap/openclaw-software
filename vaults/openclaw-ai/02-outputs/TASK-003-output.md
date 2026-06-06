# TASK-003 - Hàm tính trung vị Python

## Mục tiêu
Viết hàm `tinh_trung_vi(data)` để tính trung vị của danh sách số.

## Code

```python
def tinh_trung_vi(data):
    """Tính trung vị của danh sách số."""
    if not data:
        raise ValueError("Danh sách không được rỗng")

    sap_xep = sorted(data)
    n = len(sap_xep)
    giua = n // 2

    if n % 2 == 1:
        return sap_xep[giua]

    return (sap_xep[giua - 1] + sap_xep[giua]) / 2


# Ví dụ chạy thử
print(tinh_trung_vi([3, 1, 2]))       # 2
print(tinh_trung_vi([4, 1, 2, 3]))    # 2.5
```

## Ghi chú xác minh
- Danh sách lẻ `[3, 1, 2]` trả về `2`.
- Danh sách chẵn `[4, 1, 2, 3]` trả về `2.5`.
- Hàm sắp xếp dữ liệu trước khi tính nên không yêu cầu đầu vào đã được sắp xếp.
- Danh sách rỗng được xử lý bằng `ValueError` để tránh lỗi logic âm thầm.
