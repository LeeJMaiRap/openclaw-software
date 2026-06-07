# TASK-027 — REST API bằng http.server

## Kết quả

Đã tạo file:

```text
/data/workspace/openclaw-ai/simple_rest_api.py
```

## Chức năng

- Khởi tạo HTTP server bằng `HTTPServer` và `BaseHTTPRequestHandler` từ `http.server`.
- `GET /health` trả JSON `{"status": "ok"}` với HTTP `200`.
- `GET /items` trả danh sách item với HTTP `200`.
- `POST /items` nhận JSON `{"name": "..."}`, tạo item, trả HTTP `201`.
- Input không hợp lệ trả HTTP `400` và JSON error.
- Route không tồn tại trả HTTP `404` và JSON error.
- Response có header `Content-Type: application/json`.

## Verification notes

- File mã nguồn Python chạy được và khởi tạo HTTP server bằng `http.server`.
- API xử lý endpoint đã đặc tả.
- Response JSON hợp lệ, Content-Type đúng.
- Có xử lý input không hợp lệ với mã lỗi HTTP phù hợp.
