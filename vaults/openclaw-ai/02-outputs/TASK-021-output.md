# TASK-021 — Module todo list với JSON

## Kết quả
Đã xây dựng module todo list tối giản cho Sprint 5.

## File đã tạo
- `todo.py`
- `tests/test_todo.py`

## Chức năng chính
- `TodoList.add(content)`:
  - thêm todo mới vào danh sách trong bộ nhớ
  - sinh `id` dạng `todo-<time_ns>`
  - đặt `completed = False`
  - lưu lại file JSON
- `TodoList.delete(todo_id)`:
  - xóa todo theo `id`
  - trả `True` nếu xóa thành công
  - trả `False` nếu không tìm thấy
  - lưu lại file JSON sau khi xóa
- `TodoList.mark_complete(todo_id)`:
  - đánh dấu todo đang tồn tại là hoàn thành
  - trả todo đã cập nhật
  - trả `None` nếu không tìm thấy
  - lưu lại file JSON sau khi cập nhật
- `TodoList.save_to_file()`:
  - ghi danh sách todo ra file JSON
  - dùng cấu trúc mảng object
- `TodoList.read_from_file()`:
  - đọc lại danh sách todo từ file JSON
  - file chưa tồn tại hoặc rỗng trả `[]`

## API hàm tiện ích
- `add_todo(content, file_path)`
- `delete_todo(todo_id, file_path)`
- `mark_todo_complete(todo_id, file_path)`
- `get_all_todos(file_path)`
- `read_todos_from_file(file_path)`
- `save_todos_to_file(todos, file_path)`

## Cấu trúc dữ liệu
```json
{
  "id": "todo-001",
  "content": "Mua sữa",
  "completed": false
}
```

File JSON lưu dạng mảng:
```json
[
  {
    "id": "todo-001",
    "content": "Mua sữa",
    "completed": false
  }
]
```

## Verification notes
- Đã thêm unit test cho thêm todo và giữ trong bộ nhớ.
- Đã thêm unit test cho xóa todo theo `id`.
- Đã thêm unit test cho đánh dấu hoàn thành todo đang tồn tại.
- Đã thêm unit test cho ghi/đọc JSON đúng cấu trúc.
- Đã kiểm tra file chưa tồn tại hoặc rỗng trả `[]`.
- Lệnh kiểm thử đã chạy:

```bash
python3 -m unittest discover -s tests
```

Kết quả:

```text
Ran 20 tests in 0.018s
OK
```
