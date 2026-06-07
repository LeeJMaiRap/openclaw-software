# TASK-022 - Unit test module todo

## Kết quả
- Đã tạo bộ unit test cho `todo.py` tại `tests/test_todo.py`.
- Có test riêng cho:
  - Thêm todo: `test_add_todo_keeps_item_in_memory_and_file`
  - Xóa todo: `test_delete_todo_by_id`
  - Đánh dấu hoàn thành: `test_mark_existing_todo_complete`
- Có test kiểm tra lưu JSON đúng cấu trúc: `test_save_todos_writes_expected_json_structure`
- Có test kiểm tra đọc JSON khôi phục đúng danh sách todo: `test_read_todos_restores_list_from_json_file`
- Có thêm test cho file thiếu/rỗng và API hàm tiện ích.

## Ghi chú xác minh
- Lệnh chạy: `python3 -m unittest tests.test_todo -v`
- Kết quả: `Ran 7 tests ... OK`
- Ghi chú: `python3 -m pytest tests/test_todo.py -q` không chạy được vì môi trường chưa cài `pytest`; test dùng `unittest` chuẩn của Python nên vẫn chạy pass.
