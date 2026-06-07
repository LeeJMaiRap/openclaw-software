# TASK-018 - Benchmark bubble sort và quick sort

## Tệp mã
- `/data/workspace/openclaw-ai/benchmark_sorting.py`

## Mô tả
Đã tạo benchmark đơn giản cho Sprint 5:
- Dùng cùng bộ dữ liệu đầu vào cho `bubble_sort` và `quick_sort`.
- Chạy theo các kích thước dữ liệu: `100`, `500`, `1000`.
- Dữ liệu sinh bằng seed cố định để kết quả có thể lặp lại.
- Trước khi ghi nhận thời gian, benchmark kiểm tra kết quả sắp xếp bằng `sorted(dataset)`.
- Nếu thuật toán trả kết quả sai, benchmark dừng bằng `AssertionError`.

## Cách chạy
```bash
cd /data/workspace/openclaw-ai
python3 benchmark_sorting.py
```

## Kết quả mẫu
```text
Kết quả benchmark sắp xếp
Kích thước | Thuật toán | Thời gian (ms) | Hợp lệ
-------------------------------------------------------
       100 | Bubble sort |          0.172 | có
       100 | Quick sort  |          0.095 | có
       500 | Bubble sort |          5.132 | có
       500 | Quick sort  |          0.527 | có
      1000 | Bubble sort |         20.988 | có
      1000 | Quick sort  |          0.968 | có
```

Lưu ý: thời gian chạy có thể thay đổi theo máy và tải hệ thống.

## Ghi chú xác minh
- Đã chạy `python3 benchmark_sorting.py`: benchmark in thời gian cho cả 2 thuật toán theo từng kích thước dữ liệu.
- Đã chạy `python3 -m unittest discover -s tests`: 14 test pass.
