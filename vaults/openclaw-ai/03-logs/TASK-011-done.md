# TASK-011 - Hoàn thành

## Thời gian
2026-06-06 20:48 UTC

## Công việc đã làm
- Tạo file `prime.py` chứa hàm `is_prime(n)` theo kết quả TASK-010 để test có module import được.
- Tạo file `tests/test_prime.py` dùng `unittest`.
- Thêm test cho `n < 2`: số âm, `0`, `1`.
- Thêm test cho số nguyên tố: `2`, `3`, `17`.
- Thêm test cho hợp số: `4`, `9`, `21`.
- Ghi output vào `/data/workspace/openclaw-ai/vaults/openclaw-ai/02-outputs/TASK-011-output.md`.

## Xác minh
Đã chạy:

```bash
python3 -m unittest tests/test_prime.py
```

Kết quả:

```text
...
----------------------------------------------------------------------
Ran 3 tests in 0.000s

OK
```

## Trạng thái
Hoàn thành. Tất cả acceptance criteria đạt.
