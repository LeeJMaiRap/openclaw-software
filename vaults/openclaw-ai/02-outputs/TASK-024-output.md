# TASK-024 — Hàm đảo ngược chuỗi

## Kết quả

Đã tạo file:

```text
/data/workspace/openclaw-ai/reverse_string.py
```

Nội dung chính:

```python
def reverse_string(text: str) -> str:
    """Return the input string reversed."""
    return text[::-1]
```

## Xác minh theo acceptance criteria

- Có 1 hàm Python nhận 1 tham số kiểu chuỗi và trả về chuỗi đảo ngược: `reverse_string(text: str) -> str`.
- Hàm xử lý đúng chuỗi thường, chuỗi rỗng và chuỗi 1 ký tự nhờ slicing `text[::-1]`.
- Mã chạy được, không có lỗi cú pháp.
