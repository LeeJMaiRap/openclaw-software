# 02-outputs

Thư mục này lưu output cuối cùng của Worker cho từng task.

Quy ước tên file:

```text
TASK-xxx-output.md
```

Output nên ghi rõ:

- việc đã làm
- file code/test/tài liệu đã tạo hoặc sửa
- cách kiểm chứng
- kết quả test/lint/check liên quan
- lưu ý còn tồn đọng nếu có

Checker dùng các file này cùng done log để đối chiếu acceptance criteria. Worker phải ghi đúng đường dẫn tuyệt đối được nêu trong task prompt.
