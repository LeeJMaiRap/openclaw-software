# TASK-002 Done Log

- Task ID: TASK-002
- Project: openclaw-ai
- Batch ID: B-001
- Completed at: 2026-06-06 09:24 UTC

## Nội dung đã hoàn thành

- Viết hàm Python `tinh_trung_binh(data)` để tính trung bình cộng.
- Thêm xử lý danh sách rỗng bằng `ValueError` với thông báo rõ ràng.
- Thêm ví dụ chạy thử cho `[1, 2, 3]`, `[2, 4, 6, 8]`, và `[]`.
- Thêm giải thích ngắn cách hoạt động.

## Xác minh

Đã kiểm tra logic bằng ví dụ trong output:

- `tinh_trung_binh([1, 2, 3]) == 2.0`
- `tinh_trung_binh([2, 4, 6, 8]) == 5.0`
- `tinh_trung_binh([])` báo `ValueError` rõ ràng
