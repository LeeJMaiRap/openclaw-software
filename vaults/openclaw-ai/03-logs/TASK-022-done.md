# TASK-022 done log

## Thời gian
- Hoàn thành: 2026-06-07 05:01 UTC

## Việc đã làm
- Kiểm tra module `todo.py`.
- Tạo/cập nhật `tests/test_todo.py` với 7 unit test cho chức năng chính và lưu/đọc JSON.
- Chạy xác minh bằng `unittest`.

## Xác minh
```bash
python3 -m unittest tests.test_todo -v
```

Kết quả:
```text
Ran 7 tests in 0.009s

OK
```

## Ghi chú
- `pytest` chưa có trong môi trường (`No module named pytest`), nên dùng `unittest` theo thư viện chuẩn Python.
