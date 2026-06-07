# TASK-019 - So sánh benchmark bubble sort và quick sort

## So sánh độ phức tạp
- **Bubble sort**
  - Trung bình: `O(n^2)`
  - Xấu nhất: `O(n^2)`
- **Quick sort**
  - Trung bình: `O(n log n)`
  - Xấu nhất: `O(n^2)`

## Nhận xét từ benchmark
Kết quả chạy thực tế từ `python3 benchmark_sorting.py`:

| Kích thước | Bubble sort (ms) | Quick sort (ms) |
|---|---:|---:|
| 100 | 0.167 | 0.089 |
| 500 | 5.139 | 1.017 |
| 1000 | 20.863 | 0.906 |

Nhận xét ngắn:
- Ở mọi kích thước đo, **quick sort đều nhanh hơn bubble sort**.
- Khi dữ liệu tăng từ `100` lên `1000`, thời gian của **bubble sort tăng rất mạnh**, phù hợp với xu hướng `O(n^2)`.
- **Quick sort tăng chậm hơn nhiều** trong benchmark, phù hợp với xu hướng `O(n log n)` ở trường hợp trung bình.
- Chênh lệch hiệu năng rõ nhất ở dữ liệu lớn hơn, nên khác biệt thực tế càng dễ thấy khi số phần tử tăng.

## Giải thích khác biệt
- **Bubble sort** hoạt động bằng cách so sánh và đổi chỗ nhiều cặp phần tử kề nhau qua nhiều lượt lặp. Vì vậy số phép so sánh và đổi chỗ rất lớn khi mảng dài.
- **Quick sort** chia mảng thành các phần nhỏ quanh pivot rồi sắp xếp đệ quy. Cách chia để xử lý từng phần giúp giảm nhiều phép xử lý dư thừa trong đa số trường hợp.
- Dù quick sort có thể rơi vào `O(n^2)` ở trường hợp xấu nhất, hiệu năng trung bình vẫn tốt hơn bubble sort rất nhiều, nên thực tế thường nhanh hơn.

## Ưu và nhược điểm
### Bubble sort
**Ưu điểm**
- Dễ hiểu, dễ cài đặt.
- Phù hợp cho bài học nhập môn hoặc dữ liệu rất nhỏ.

**Nhược điểm**
- Rất chậm khi dữ liệu tăng.
- Tốn nhiều phép so sánh và đổi chỗ.
- Kém hiệu quả trong đa số bài toán thực tế.

### Quick sort
**Ưu điểm**
- Nhanh trong đa số trường hợp thực tế.
- Phù hợp hơn cho tập dữ liệu vừa và lớn.
- Hiệu năng trung bình tốt hơn rõ rệt.

**Nhược điểm**
- Cài đặt phức tạp hơn bubble sort.
- Có trường hợp xấu nhất `O(n^2)` nếu chọn pivot không tốt.
- Thường dùng đệ quy, nên cần chú ý ngăn xếp lời gọi.

## Kết luận
- **Nên dùng quick sort** khi cần sắp xếp dữ liệu thực tế vì hiệu năng trung bình tốt hơn, mở rộng tốt hơn khi kích thước đầu vào tăng.
- **Bubble sort kém hiệu quả hơn trong đa số trường hợp** vì phải lặp và đổi chỗ quá nhiều, làm thời gian tăng rất nhanh theo số phần tử.
- **Bubble sort** chỉ nên dùng khi mục tiêu chính là học thuật toán cơ bản hoặc xử lý dữ liệu rất nhỏ.

## Ghi chú xác minh
- Đã chạy `python3 benchmark_sorting.py` và ghi lại số đo thực tế.
- Đã chạy `python3 -m unittest discover -s tests`.
- Kết quả xác minh: `Ran 14 tests ... OK`.
