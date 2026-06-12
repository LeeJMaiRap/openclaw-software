# TASK-044 — Đặc tả hàm đếm số nguyên tố trong list số nguyên

## Mục tiêu
Xây dựng hàm Python nhận vào một list số nguyên và trả về số lượng phần tử là số nguyên tố trong list đó.

## Interface dự kiến
```python
def count_primes(numbers: list[int]) -> int:
    ...
```

## Đầu vào
- `numbers`: `list[int]`
- Mỗi phần tử trong list là một số nguyên.
- Sprint 5 giữ phạm vi đơn giản: giả định dữ liệu đầu vào đúng kiểu theo interface.

## Đầu ra
- Trả về `int`
- Giá trị trả về là số lượng phần tử trong `numbers` thỏa điều kiện là số nguyên tố.

## Quy tắc xác định số nguyên tố
Một phần tử được tính là số nguyên tố nếu:
- Là số nguyên dương lớn hơn `1`
- Chỉ có đúng `2` ước dương: `1` và chính nó

## Cách xử lý giá trị không phải số nguyên tố
Các giá trị sau **không** được tính là số nguyên tố:
- Số âm
- `0`
- `1`

Ví dụ:
- `-5` → không tính
- `0` → không tính
- `1` → không tính
- `2` → tính
- `3` → tính
- `4` → không tính

## Phạm vi xử lý
- Chỉ xử lý bài toán: đếm bao nhiêu phần tử là số nguyên tố trong một list số nguyên.
- Không yêu cầu:
  - Làm sạch dữ liệu
  - Ép kiểu
  - Xử lý input không phải `list[int]`
  - Tối ưu nâng cao ngoài mức phù hợp Sprint 5

## Ví dụ kỳ vọng
```python
count_primes([2, 3, 4, 5, 1, 0, -7]) == 3
count_primes([4, 6, 8, 9]) == 0
count_primes([]) == 0
```

## Kết luận cho task code
Task code nên bám theo interface sau:
```python
def count_primes(numbers: list[int]) -> int:
    ...
```

Hàm này duyệt qua list đầu vào, kiểm tra từng phần tử có phải số nguyên tố hay không, rồi trả về tổng số phần tử nguyên tố.
