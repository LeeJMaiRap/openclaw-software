# TASK-032 - Đặc tả hàm tính tổng số chẵn

## Mục tiêu

Xác định đầu vào, đầu ra và phạm vi xử lý cho hàm Python tính tổng các số chẵn trong một danh sách.

## Đầu vào

- Hàm nhận **1 danh sách số**.
- Mỗi phần tử trong danh sách là một số có thể kiểm tra tính chẵn bằng phép chia dư.

Ví dụ:

```python
[1, 2, 3, 4, 6]
```

## Đầu ra

- Hàm trả về **tổng các phần tử chẵn** trong danh sách.
- Kết quả là một số.

Ví dụ:

```python
[1, 2, 3, 4, 6] -> 12
```

Vì các số chẵn là `2`, `4`, `6`, tổng là `12`.

## Quy ước xác định số chẵn

Một số được xem là số chẵn nếu phép chia dư cho `2` bằng `0`:

```python
number % 2 == 0
```

## Trường hợp danh sách rỗng

Nếu danh sách đầu vào rỗng, hàm phải trả về `0`.

Ví dụ:

```python
[] -> 0
```

Lý do: không có phần tử nào để cộng, nên tổng mặc định là `0`.

## Phạm vi xử lý

Hàm chỉ cần:

1. Duyệt qua các phần tử trong danh sách.
2. Kiểm tra phần tử nào là số chẵn bằng `number % 2 == 0`.
3. Cộng các phần tử chẵn.
4. Trả về tổng cuối cùng.

## Ví dụ hàm Python

```python
def sum_even_numbers(numbers):
    total = 0

    for number in numbers:
        if number % 2 == 0:
            total += number

    return total
```

## Ví dụ kiểm tra

```python
sum_even_numbers([1, 2, 3, 4, 6])  # 12
sum_even_numbers([1, 3, 5])        # 0
sum_even_numbers([])               # 0
```
