# TASK-002 - Hàm `tinh_trung_binh(data)`

## Code Python

```python
def tinh_trung_binh(data):
    if len(data) == 0:
        raise ValueError("Danh sách rỗng, không thể tính trung bình cộng.")
    return sum(data) / len(data)


# Ví dụ chạy thử
print(tinh_trung_binh([1, 2, 3]))       # 2.0
print(tinh_trung_binh([2, 4, 6, 8]))    # 5.0

try:
    print(tinh_trung_binh([]))
except ValueError as loi:
    print(loi)
```

## Kết quả mong đợi

```text
2.0
5.0
Danh sách rỗng, không thể tính trung bình cộng.
```

## Giải thích ngắn

Hàm `tinh_trung_binh(data)` kiểm tra danh sách đầu vào. Nếu danh sách rỗng, hàm báo lỗi rõ ràng bằng `ValueError`. Nếu danh sách có dữ liệu, hàm lấy tổng các số bằng `sum(data)` rồi chia cho số phần tử bằng `len(data)`.

## Ghi chú xác minh

- `[1, 2, 3]` trả về `2.0`.
- `[2, 4, 6, 8]` trả về `5.0`.
- `[]` được xử lý bằng lỗi rõ ràng.
