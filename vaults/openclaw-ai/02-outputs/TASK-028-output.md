# TASK-028 — Unit test REST API

## Kết quả

Đã tạo file test riêng:

```text
/data/workspace/openclaw-ai/tests/test_simple_rest_api.py
```

## Test cases

- `GET /health` thành công: HTTP `200`, JSON `{"status": "ok"}`.
- `POST /items` thành công: HTTP `201`, JSON chứa item được tạo.
- `POST /items` lỗi validation: HTTP `400`, JSON `{"error": "name is required"}`.
- `GET /missing` lỗi route: HTTP `404`, JSON `{"error": "not found"}`.

## Verification output

```text
test_create_item_success (tests.test_simple_rest_api.SimpleRestApiTests.test_create_item_success) ... ok
test_create_item_validation_error (tests.test_simple_rest_api.SimpleRestApiTests.test_create_item_validation_error) ... ok
test_health_success (tests.test_simple_rest_api.SimpleRestApiTests.test_health_success) ... ok
test_not_found_error (tests.test_simple_rest_api.SimpleRestApiTests.test_not_found_error) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.001s

OK
```

## Acceptance criteria

- Unit test là task riêng và nằm trong file tách biệt mã nguồn chính.
- Có ca thành công và ca lỗi.
- Test xác minh mã trạng thái HTTP và nội dung JSON response.
- Toàn bộ test chạy pass bằng `unittest`.
