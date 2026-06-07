# TASK-017 done log

## Thời gian
- 2026-06-07 04:51 UTC

## Công việc đã làm
- Kiểm tra mã nguồn `sorting.py` từ `TASK-016`.
- Tạo file unit test riêng: `tests/test_sorting_correctness.py`.
- Bổ sung test cho `bubble_sort` và `quick_sort` với mảng rỗng, 1 phần tử, đã sắp xếp, đảo ngược và có phần tử trùng lặp.

## Xác minh
- `python`: không có trong môi trường.
- `python3 -m pytest tests/test_sorting_correctness.py tests/test_sorting.py`: thất bại vì chưa cài `pytest`.
- `python3 -m unittest tests.test_sorting_correctness tests.test_sorting`: thành công.
- Kết quả unittest: `Ran 6 tests ... OK`.

## Trạng thái
- Hoàn thành.
