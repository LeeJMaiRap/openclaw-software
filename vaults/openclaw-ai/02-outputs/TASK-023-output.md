# TASK-023

## Phạm vi
Viết 1 hàm Python nhận vào **chuỗi** (`str`) và trả về **chuỗi đảo ngược**.

Ví dụ:
```python
def dao_nguoc_chuoi(s: str) -> str:
    return s[::-1]
```

## Kết quả mong đợi
- Input: 1 chuỗi
- Output: chuỗi mới với thứ tự ký tự bị đảo ngược

Ví dụ:
- `"hello"` → `"olleh"`
- `"abc 123"` → `"321 cba"`

## Tiêu chí kiểm thử cần có
1. **Chuỗi thường**  
   - Input: `"hello"`  
   - Output mong đợi: `"olleh"`

2. **Chuỗi rỗng**  
   - Input: `""`  
   - Output mong đợi: `""`

3. **Chuỗi 1 ký tự**  
   - Input: `"a"`  
   - Output mong đợi: `"a"`

4. **Chuỗi có khoảng trắng**  
   - Input: `"xin chao"`  
   - Output mong đợi: `"oahc nix"`

5. **Chuỗi có ký tự đặc biệt**  
   - Input: `"a! b@"`  
   - Output mong đợi: `"@b !a"`

## Ghi chú xác minh
- Phạm vi đã giới hạn ở 1 hàm Python đơn giản cho Sprint 5.
- Đã nêu rõ input là chuỗi, output là chuỗi đảo ngược.
- Đã liệt kê đủ các case test theo yêu cầu: chuỗi thường, rỗng, 1 ký tự, có khoảng trắng, có ký tự đặc biệt.
