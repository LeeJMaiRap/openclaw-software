# TASK-015 — Phạm vi benchmark bubble sort và quick sort

## Mục tiêu
Xác định phạm vi benchmark tối thiểu cho Sprint 5 để các task code bám theo, giữ đơn giản và nhất quán.

## Thuật toán cần có
1. **Bubble sort**
2. **Quick sort**

Không mở rộng thêm thuật toán khác trong Sprint 5.

## Dữ liệu benchmark
Dùng cùng một cách sinh dữ liệu cho cả 2 thuật toán để so sánh công bằng.

### Kích thước dữ liệu tối thiểu
Chọn ít nhất 3 mức:
- **1,000 phần tử**
- **5,000 phần tử**
- **10,000 phần tử**

Có thể giữ đúng 3 mức này cho bản đầu tiên.

### Cách sinh dữ liệu
- Kiểu dữ liệu: **mảng số nguyên**
- Miền giá trị: số nguyên trong khoảng **0 đến 100,000**
- Dùng **seed cố định** cho bộ sinh số ngẫu nhiên để lần chạy khác vẫn ra cùng dữ liệu
- Với mỗi kích thước `n`, sinh **1 mảng gốc**
- Trước khi chạy từng thuật toán, **copy từ mảng gốc** để bảo đảm cả bubble sort và quick sort nhận cùng đầu vào

### Bộ dữ liệu đề xuất
Để giữ đơn giản cho Sprint 5:
- Mặc định benchmark trên **dữ liệu ngẫu nhiên**
- Chưa bắt buộc tách thêm best case / worst case

Nếu cần ghi rõ hơn trong task code:
- `input_1000`
- `input_5000`
- `input_10000`

## Chỉ số cần đo
Mỗi lần benchmark phải có tối thiểu 2 nhóm đầu ra:

### 1. Thời gian chạy
- Đơn vị: **milliseconds (ms)** hoặc **nanoseconds rồi quy đổi rõ ràng**
- Đo riêng cho từng thuật toán trên từng kích thước dữ liệu

Ví dụ cột kết quả:
- `algorithm`
- `input_size`
- `execution_time_ms`

### 2. Kiểm tra tính đúng
Sau khi sắp xếp, cần kiểm tra:
- Mảng kết quả có **không giảm dần**
- Kết quả của thuật toán **trùng với kết quả sort chuẩn** của ngôn ngữ hoặc hàm kiểm tra tương đương

Ví dụ cột kết quả:
- `is_sorted`
- `matches_expected`

## Cấu trúc kết quả nên có
Nên trả kết quả theo từng dòng benchmark, ví dụ:

| algorithm | input_size | execution_time_ms | is_sorted | matches_expected |
|---|---:|---:|---|---|
| bubble_sort | 1000 | ... | true | true |
| quick_sort | 1000 | ... | true | true |
| bubble_sort | 5000 | ... | true | true |
| quick_sort | 5000 | ... | true | true |
| bubble_sort | 10000 | ... | true | true |
| quick_sort | 10000 | ... | true | true |

## Quy ước để task code bám theo
- Chỉ benchmark **2 thuật toán**: bubble sort, quick sort
- Dùng **cùng seed**, **cùng cách sinh dữ liệu**, **cùng input gốc** cho mọi lần so sánh
- Mỗi thuật toán chạy trên ít nhất **3 kích thước dữ liệu**: 1000, 5000, 10000
- Mỗi kết quả phải có **thời gian chạy** và **xác nhận đúng kết quả sắp xếp**
- Sprint 5 ưu tiên **đơn giản, dễ lặp lại, dễ đọc kết quả**

## Ghi chú verification
- Nội dung đã bao phủ đủ: 2 thuật toán, ít nhất 3 kích thước dữ liệu, cách sinh input nhất quán, thời gian chạy, kiểm tra tính đúng.
