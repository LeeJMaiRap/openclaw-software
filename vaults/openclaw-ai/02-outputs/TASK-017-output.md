# TASK-017 - Bộ unit test cho bubble sort và quick sort

## Kết quả
- Đã tạo test riêng tại `tests/test_sorting_correctness.py`.
- Test kiểm tra cả `bubble_sort` và `quick_sort` qua các trường hợp:
  - Mảng rỗng: `[]`
  - Mảng 1 phần tử: `[7]`
  - Mảng đã sắp xếp: `[1, 2, 3, 4, 5]`
  - Mảng đảo ngược: `[5, 4, 3, 2, 1]`
  - Mảng có phần tử trùng lặp: `[3, 1, 2, 3, 1]`
- Task test được tách riêng và phụ thuộc trực tiếp `TASK-016` theo `tasks/TASK-017.json`.

## Ghi chú xác minh
- Lệnh pytest không chạy được vì môi trường chưa cài `pytest`.
- Đã xác minh bằng `unittest` có sẵn trong Python:
  - `python3 -m unittest tests.test_sorting_correctness tests.test_sorting`
  - Kết quả: `Ran 6 tests ... OK`
