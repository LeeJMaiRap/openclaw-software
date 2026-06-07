# TASK-012

## Hành vi script Python

### 1. Đầu vào
- Nhận 1 tham số đường dẫn tới file CSV.
- Giả định đơn giản cho Sprint 5:
  - Mã hóa ưu tiên: `UTF-8`.
  - Phân tách phổ biến: dấu phẩy `,`.
  - Dòng đầu là header chứa tên cột.

### 2. Quy tắc xử lý dữ liệu
- Đọc từng cột theo tên cột trong header.
- Xem cột là **cột số hợp lệ** nếu các giá trị cần cộng trong cột có thể chuyển sang kiểu số (`int` hoặc `float`).
- Với mỗi cột số hợp lệ:
  - Cộng dồn toàn bộ giá trị số trong cột.
- Cột không phải số thì bỏ qua, không đưa vào kết quả.
- Giá trị rỗng, chữ, hoặc dữ liệu không đổi sang số được:
  - Không tính vào tổng.
  - Không làm cột văn bản trở thành cột số.

### 3. Định dạng output mong muốn
Output nên là danh sách tên cột và tổng tương ứng.

Ví dụ dạng JSON:

```json
{
  "col_a": 150,
  "col_b": 27.5,
  "col_c": 999
}
```

Hoặc nếu in ra console, mỗi dòng 1 cột:

```text
col_a: 150
col_b: 27.5
col_c: 999
```

## Ghi chú đơn giản hóa
- Chưa cần xử lý nhiều loại delimiter khác ngoài `,`.
- Chưa cần suy luận kiểu dữ liệu phức tạp.
- Mục tiêu Sprint 5: rõ, dễ làm, dễ test.

## Verification notes
- Đã đối chiếu đủ 3 tiêu chí acceptance:
  1. Có mô tả đầu vào, encoding, delimiter.
  2. Có quy tắc nhận diện cột số và bỏ qua cột không phải số.
  3. Có định dạng output gồm tên cột và tổng tương ứng.
