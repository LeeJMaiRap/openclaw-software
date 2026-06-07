# TASK-031 — Unit test `factorial`

## Kết quả

Đã tạo file test riêng:

```text
/data/workspace/openclaw-ai/tests/test_factorial.py
```

## Test cases

- `factorial(0) == 1`
- `factorial(1) == 1`
- `factorial(5) == 120`
- `factorial(-1)` raise `ValueError`

## Verification output

```text
test_five (tests.test_factorial.FactorialTests.test_five) ... ok
test_negative_number_raises_value_error (tests.test_factorial.FactorialTests.test_negative_number_raises_value_error) ... ok
test_one (tests.test_factorial.FactorialTests.test_one) ... ok
test_zero (tests.test_factorial.FactorialTests.test_zero) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
```

## Acceptance criteria

- Có file unit test riêng cho hàm `factorial`.
- Test bao phủ ít nhất các trường hợp `0`, `1`, `5`.
- Toàn bộ test chạy pass với hàm đã viết.
- Test có thể chạy bằng framework unit test chuẩn của Python: `unittest`.
