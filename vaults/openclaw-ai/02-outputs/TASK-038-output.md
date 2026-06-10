# TASK-038 - Quy tắc chuyển số La Mã sang số nguyên

## 1. Ký tự La Mã cần hỗ trợ

Hàm cần hỗ trợ đúng 7 ký tự sau:

| Ký tự | Giá trị |
|---|---:|
| I | 1 |
| V | 5 |
| X | 10 |
| L | 50 |
| C | 100 |
| D | 500 |
| M | 1000 |

Chỉ nhận chữ in hoa: `I`, `V`, `X`, `L`, `C`, `D`, `M`.

## 2. Quy tắc chuyển đổi

### Quy tắc cộng

Đọc chuỗi từ trái sang phải.

Nếu giá trị ký tự hiện tại lớn hơn hoặc bằng giá trị ký tự bên phải, cộng giá trị ký tự hiện tại vào tổng.

Ví dụ:

- `III` = 1 + 1 + 1 = 3
- `VI` = 5 + 1 = 6
- `XII` = 10 + 1 + 1 = 12
- `LX` = 50 + 10 = 60

### Quy tắc trừ

Nếu giá trị ký tự hiện tại nhỏ hơn giá trị ký tự ngay bên phải, xử lý như một cặp trừ: lấy giá trị bên phải trừ giá trị hiện tại, rồi bỏ qua cả hai ký tự.

Chỉ hỗ trợ 6 cặp trừ hợp lệ:

| Cặp | Giá trị |
|---|---:|
| IV | 4 |
| IX | 9 |
| XL | 40 |
| XC | 90 |
| CD | 400 |
| CM | 900 |

Ví dụ:

- `IV` = 5 - 1 = 4
- `IX` = 10 - 1 = 9
- `XL` = 50 - 10 = 40
- `XC` = 100 - 10 = 90
- `CD` = 500 - 100 = 400
- `CM` = 1000 - 100 = 900
- `MCMXCIV` = 1000 + 900 + 90 + 4 = 1994

## 3. Phạm vi đầu vào mục tiêu

Cho Sprint 5, giữ hàm đơn giản và nhất quán:

- Đầu vào là chuỗi không rỗng.
- Chỉ chứa ký tự in hoa thuộc tập `I`, `V`, `X`, `L`, `C`, `D`, `M`.
- Hỗ trợ số La Mã chuẩn trong phạm vi `1` đến `3999`.
- Không cần hỗ trợ chữ thường.
- Không cần hỗ trợ khoảng trắng đầu/cuối hoặc ký tự phân tách.
- Không cần hỗ trợ số 0, số âm, số thập phân.
- Nếu gặp ký tự không hợp lệ hoặc cặp trừ không thuộc 6 cặp hợp lệ, hàm nên báo lỗi hoặc trả kết quả lỗi theo quy ước chung của codebase.

## Gợi ý xử lý đơn giản

Một cách code dễ hiểu:

1. Tạo bảng giá trị cho 7 ký tự.
2. Duyệt chuỗi từ trái sang phải.
3. Nếu ký tự hiện tại và ký tự kế tiếp tạo thành một trong 6 cặp trừ hợp lệ, cộng giá trị cặp đó và nhảy 2 bước.
4. Ngược lại, cộng giá trị ký tự hiện tại và nhảy 1 bước.
5. Trước khi tính, kiểm tra chuỗi không rỗng và mọi ký tự đều hợp lệ.
