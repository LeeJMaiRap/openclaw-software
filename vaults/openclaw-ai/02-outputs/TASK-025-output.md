# TASK-025 — Unit test hàm đảo ngược chuỗi

## Kết quả

Đã tạo file:

```text
/data/workspace/openclaw-ai/tests/test_reverse_string.py
```

## Test cases

- Chuỗi thường: `hello` → `olleh`
- Chuỗi rỗng: `` → ``
- Một ký tự: `a` → `a`
- Chuỗi có khoảng trắng/ký tự đặc biệt: `a b!` → `!b a`

## Xác minh acceptance criteria

- Có test cho ít nhất 4 trường hợp: chuỗi thường, chuỗi rỗng, 1 ký tự, chuỗi có khoảng trắng hoặc ký tự đặc biệt.
- Tất cả test pass khi chạy với hàm đã viết `reverse_string`.
- Test độc lập và có thể chạy bằng framework test Python phổ biến: `unittest`.

## Unittest output

```text
test_empty_string (tests.test_reverse_string.ReverseStringTests.test_empty_string) ... ok
test_regular_string (tests.test_reverse_string.ReverseStringTests.test_regular_string) ... ok
test_single_character (tests.test_reverse_string.ReverseStringTests.test_single_character) ... ok
test_spaces_and_special_characters (tests.test_reverse_string.ReverseStringTests.test_spaces_and_special_characters) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
```
