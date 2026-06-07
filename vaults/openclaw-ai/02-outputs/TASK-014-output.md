# TASK-014 - Kết quả

## Đã thực hiện
- Tạo bộ unit test cho `sum_csv_columns.py` tại `tests/test_sum_csv_columns.py`.
- Dùng framework chuẩn `unittest` của Python để giữ giải pháp đơn giản cho Sprint 5.

## Phạm vi test
1. CSV có nhiều cột số:
   - Kiểm tra tổng đúng cho từng cột `apples`, `oranges`, `pears`.
2. CSV có cột chữ:
   - Kiểm tra cột `name` bị bỏ qua.
   - Kiểm tra các cột số `score`, `bonus` vẫn được tính tổng đúng.

## Ghi chú xác minh
- Lệnh chạy:

```bash
python3 -m unittest tests/test_sum_csv_columns.py -v
```

- Kết quả: 2 test pass.
