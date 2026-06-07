# TASK-013 - Script tính tổng cột số trong CSV

## Kết quả

Đã tạo script Python:

- `/data/workspace/openclaw-ai/sum_csv_columns.py`

## Cách chạy

```bash
python3 /data/workspace/openclaw-ai/sum_csv_columns.py duong_dan_file.csv
```

## Chức năng

- Nhận đường dẫn file CSV từ dòng lệnh.
- Đọc CSV bằng thư viện chuẩn `csv`.
- Tính tổng cho từng cột có dữ liệu số.
- Bỏ qua cột không phải số, không làm dừng chương trình.
- Hỗ trợ Python 3.

## Ví dụ kiểm thử

File mẫu:

```csv
ten,tuoi,diem,ghi_chu
An,20,8.5,tot
Binh,21,7.25,kha
Chi,,9.25,gioi
```

Lệnh chạy:

```bash
python3 /data/workspace/openclaw-ai/sum_csv_columns.py /tmp/task013_sample.csv
```

Kết quả:

```text
tuoi: 41
diem: 25
```

## Ghi chú xác minh

- Cột `ten` và `ghi_chu` bị bỏ qua vì không phải số.
- Cột `tuoi` tính tổng các giá trị số, bỏ qua ô trống.
- Cột `diem` tính đúng tổng số thập phân.
