# TASK-026 — Phạm vi REST API dùng http.server

## Endpoint

1. `GET /health`
   - Request body: không có
   - Response `200 application/json`:
     ```json
     {"status": "ok"}
     ```

2. `GET /items`
   - Request body: không có
   - Response `200 application/json`:
     ```json
     {"items": []}
     ```

3. `POST /items`
   - Request body `application/json`:
     ```json
     {"name": "demo"}
     ```
   - Response `201 application/json`:
     ```json
     {"item": {"id": 1, "name": "demo"}}
     ```
   - Invalid input response `400 application/json`:
     ```json
     {"error": "name is required"}
     ```

4. Unknown route
   - Response `404 application/json`:
     ```json
     {"error": "not found"}
     ```

## Ràng buộc

- Chỉ dùng Python standard library.
- Server dùng `http.server`.
- Không cần framework ngoài.

## Verification notes

- Xác định rõ ít nhất 3 endpoint REST cơ bản phù hợp cho API đơn giản: `GET /health`, `GET /items`, `POST /items`.
- Có request/response JSON và mã trạng thái HTTP cho từng endpoint.
- Không yêu cầu framework ngoài `http.server`.
