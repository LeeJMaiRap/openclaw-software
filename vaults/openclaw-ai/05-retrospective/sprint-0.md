# Retrospective — Sprint 0

## Những gì đã làm được

- Tạo cấu trúc thư mục dự án `openclaw-ai/` trong `/data/workspace`.
- Lưu tài liệu kiến trúc đã trích từ file `.docx` vào `docs/architecture/openclaw_knowledge_base_v2.txt`.
- Tạo `README.md` tiếng Anh cho repo.
- Tạo checklist nội bộ `docs/sprint-0.md` bằng tiếng Việt.
- Thiết kế và ghi `schemas/task.schema.json` theo spec task file mục 5.1.
- Viết validator Python tại `validators/validate_task.py`.
- Tạo task mẫu hợp lệ và không hợp lệ trong `tasks/examples/`.
- Cài Python 3.11.2 để chạy validator.
- Test validator thành công:
  - `valid_task.json` pass.
  - `invalid_task.json` fail với lỗi cụ thể.
- Viết `docker/Dockerfile` dùng `python:3.11-slim`.
- Tạo `.dockerignore`.
- Cập nhật `README.md` với lệnh Docker build/run.
- Build image `openclaw-ai:leej-sprint0` thành công.
- Chạy Docker smoke test thành công với output `✅ Task file hợp lệ`.
- Thiết lập Obsidian vault theo cấu trúc mục 6.1.
- Tạo `README.md` tiếng Việt trong từng thư mục vault.
- Tạo `00-overview/project.md` tóm tắt dự án OpenClaw AI.

## Vấn đề gặp phải và cách giải quyết

### 1. Brace expansion với `/bin/sh`

Vấn đề: lệnh `mkdir -p openclaw-ai/{...}` tạo thư mục sai vì runtime dùng `/bin/sh`, không hỗ trợ brace expansion như Bash.

Cách giải quyết:

- Dọn các thư mục lỗi có ký tự `{}`.
- Chạy lại bằng lệnh POSIX rõ ràng, liệt kê từng đường dẫn cần tạo.

Bài học: khi dùng `exec`, giả định shell là `/bin/sh`; tránh Bash-only syntax nếu không gọi `bash -lc` rõ ràng.

### 2. Môi trường thiếu Python 3

Vấn đề: validator yêu cầu chạy bằng `python3`, nhưng host ban đầu không có Python.

Cách giải quyết:

- Cài Python 3 bằng package manager hệ thống.
- Xác nhận version: `Python 3.11.2`.
- Chạy lại test validator.

Bài học: Sprint 1 nên ghi rõ dependency tối thiểu trong README hoặc tạo script kiểm tra môi trường.

### 3. Docker output dài và bị cắt trong chat

Vấn đề: build output Docker dài, phần trả lời đầu bị cắt.

Cách giải quyết:

- Truy xuất log còn lại từ process log.
- Show phần export image và output `docker run` riêng.

Bài học: với output dài, nên tách phần quan trọng: build result, image tag, run result, exit code.

### 4. CMD smoke test chỉ là tạm thời

Vấn đề: Dockerfile chưa chạy LeeJ Agent thật, chỉ chạy validator smoke test.

Cách giải quyết:

- Chấp nhận cho Sprint 0 vì mục tiêu là kiểm tra runtime sống và schema hợp lệ.
- Ghi rõ sau Sprint 0 sẽ thay bằng entrypoint thật của LeeJ Agent.

Bài học: smoke test đơn giản giúp phát hiện lỗi môi trường sớm; đừng bỏ qua dù chưa có app chính.

## Bài học cho Sprint 1

- Cần tạo entrypoint thật cho LeeJ Agent thay vì chỉ dùng validator smoke test.
- Cần định nghĩa adapter I/O giữa LeeJ Agent và Worker.
- Cần thêm script kiểm tra môi trường, ví dụ `scripts/check_env.sh` hoặc `make smoke`.
- Cần cân nhắc dùng Python package chuẩn hơn nếu validator mở rộng, nhưng Sprint 1 vẫn nên giữ đơn giản.
- Cần thêm task lifecycle: `pending`, `in_progress`, `blocked`, `done`, `failed`.
- Cần định nghĩa nơi lưu output và log cho mỗi task rõ ràng hơn.
- Cần tránh shell syntax phụ thuộc Bash nếu runtime không đảm bảo Bash.
- Cần giữ nguyên nguyên tắc: mỗi bước có output kiểm tra được trước khi sang bước tiếp.
