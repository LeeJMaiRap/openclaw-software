# TASK-005 - Unit test cho hàm thống kê cơ bản

## File đã tạo

- `thong_ke_co_ban.py`: chứa 3 hàm thống kê cơ bản:
  - `tinh_trung_binh(data)`
  - `tinh_trung_vi(data)`
  - `tinh_do_lech_chuan(data)`
- `tests/test_thong_ke_co_ban.py`: chứa test suite dùng Python standard library `unittest`.

## Nội dung test chính

- `tinh_trung_binh(data)` được kiểm tra với 2 bộ dữ liệu:
  - `[1, 2, 3]` → `2.0`
  - `[2, 4, 6, 8]` → `5.0`
- `tinh_trung_vi(data)` được kiểm tra với:
  - danh sách lẻ `[3, 1, 2]` → `2`
  - danh sách chẵn `[4, 1, 2, 3]` → `2.5`
- `tinh_do_lech_chuan(data)` được kiểm tra với 2 bộ dữ liệu:
  - `[2, 4, 4, 4, 5, 5, 7, 9]` → `2.0`
  - `[1, 2, 3, 4, 5]` → `sqrt(2)`

## Cách chạy

```bash
python3 -m unittest tests/test_thong_ke_co_ban.py
```

## Ghi chú xác minh

Đã chạy test suite thành công:

```text
....
----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
```

## Trạng thái acceptance criteria

- Đạt: test `tinh_trung_binh(data)` với ít nhất 2 bộ dữ liệu.
- Đạt: test `tinh_trung_vi(data)` với danh sách chẵn và lẻ.
- Đạt: test `tinh_do_lech_chuan(data)` với ít nhất 2 bộ dữ liệu và test suite chạy được.
