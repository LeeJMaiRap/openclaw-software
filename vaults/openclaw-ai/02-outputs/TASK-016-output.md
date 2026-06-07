# TASK-016 Output

## Kết quả

Đã viết mã nguồn cho 2 thuật toán sắp xếp số nguyên:

- `bubble_sort(values)` trong `sorting.py`
- `quick_sort(values)` trong `sorting.py`

Đã thêm giao diện gọi thống nhất:

- `sort(values, algorithm="quick")`
- `SORT_ALGORITHMS` để test hoặc benchmark gọi theo tên thuật toán

## Cách dùng

```python
from sorting import bubble_sort, quick_sort, sort

bubble_sort([3, 1, 2])          # [1, 2, 3]
quick_sort([3, 1, 2])           # [1, 2, 3]
sort([3, 1, 2], "bubble")      # [1, 2, 3]
sort([3, 1, 2], "quick")       # [1, 2, 3]
```

## Ghi chú kiểm chứng

- Đã thêm `tests/test_sorting.py` để kiểm tra dữ liệu rỗng, một phần tử, số âm, số trùng, và thứ tự giảm dần.
- Cả 2 hàm trả về list mới, không sửa input gốc.
- Lệnh kiểm chứng đã chạy:

```bash
python3 -m unittest tests/test_sorting.py
```

Kết quả: `Ran 5 tests ... OK`.
