# Retrospective Sprint 1

## Những gì đã làm được

- Tạo `TASK-001` cho mục tiêu viết hàm Python tính số Fibonacci thứ `n`.
- Tạo LeeJ agent/dispatcher tối thiểu cho Sprint 1.
- Worker tạo output Fibonacci bằng tiếng Việt, có code, ví dụ chạy thử và giải thích ngắn.
- Ghi log dispatch, log hoàn thành và log kiểm tra.
- Tạo `leej/checker.py` để đọc task JSON và output Markdown.
- Checker dùng keyword matching đơn giản, không gọi LLM.
- Chạy kiểm tra thành công:

```text
✅ TASK-001: 3/3 criteria passed
```

## Vấn đề gặp phải và cách giải quyết

### Model allowlist

Vấn đề:

- Worker/dispatcher bị ảnh hưởng bởi model allowlist.
- Cấu hình model không được nhận ngay trong môi trường đang chạy.

Cách giải quyết:

- Điều chỉnh allowlist cho model cần dùng.
- Restart Docker host để gateway nhận cấu hình mới.

### Gateway không hot reload qua CLI

Vấn đề:

- Gateway không hot reload được qua CLI trong môi trường này.
- Thay đổi config không có hiệu lực ngay nếu chỉ thao tác qua CLI.

Cách giải quyết:

- Ghi nhận đây là giới hạn môi trường.
- Dùng restart Docker host khi cần chắc chắn gateway nạp lại config.

### Path task/output lệch nhau

Vấn đề:

- Worker output ban đầu nằm ngoài repo project ở `/data/workspace/vaults/...`.
- Repo thật nằm tại `/data/workspace/openclaw-ai`.

Cách giải quyết:

- Copy checker/output/log vào đúng repo `openclaw-ai/` trước khi commit.
- Sprint 2 cần chuẩn hóa working directory cho worker.

## Bài học cho Sprint 2

- Chuẩn hóa repo root và working directory ngay từ đầu.
- Không giả định gateway hot reload; nếu đổi config, cần kế hoạch restart rõ.
- Checker Sprint 1 chỉ nên giữ keyword matching đơn giản, nhưng Sprint 2 nên tách rule matching thành module dễ test.
- Cần thêm test fixture cho trường hợp thiếu criteria.
- Dispatcher nên ghi rõ input path, output path, model và trạng thái để debug nhanh hơn.
- Mỗi bước nên tạo artifact trong repo project, không tạo ở workspace root trừ khi có lý do rõ.
