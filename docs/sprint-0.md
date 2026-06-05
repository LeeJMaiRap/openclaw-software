# Sprint 0 — Checklist nội bộ

## Mục tiêu

Tạo nền móng tối thiểu cho OpenClaw AI, ưu tiên đơn giản và kiểm tra được trước khi tối ưu.

## Trạng thái tổng kết

✅ Sprint 0 hoàn thành.

## Nguyên tắc thực hiện

- Mỗi bước phải có output kiểm tra được.
- Không chuyển sang bước tiếp theo nếu bước hiện tại chưa được xác nhận.
- Không tự giả định khi có điểm chưa rõ.
- Chưa cần GitHub remote hoặc push trong Sprint 0.

## ✅ Bước 1 — Cấu trúc thư mục dự án

### Việc đã làm

- [x] Tạo thư mục gốc dự án: `openclaw-ai/`
- [x] Tạo `README.md` bằng tiếng Anh.
- [x] Tạo `docs/sprint-0.md` bằng tiếng Việt.
- [x] Tạo thư mục `docs/architecture/`.
- [x] Lưu tài liệu kiến trúc đã trích tại `docs/architecture/openclaw_knowledge_base_v2.txt`.
- [x] Tạo thư mục `schemas/` cho JSON Schema task file.
- [x] Tạo thư mục `validators/` cho validator task file.
- [x] Tạo thư mục `tasks/examples/` cho task mẫu.
- [x] Tạo thư mục `docker/` cho Dockerfile LeeJ Agent.
- [x] Tạo Obsidian vault tại `vaults/openclaw-ai/`.

### Ghi chú thực tế

- Lần đầu dùng brace expansion với `/bin/sh`, tạo ra thư mục sai vì `/bin/sh` không expand brace như Bash.
- Đã dọn thư mục lỗi và chạy lại bằng lệnh POSIX `mkdir -p` tường minh.

## ✅ Bước 2 — JSON Schema + validator task file

### Việc đã làm

- [x] Tạo `schemas/task.schema.json`.
- [x] Tạo `validators/validate_task.py`.
- [x] Tạo `tasks/examples/valid_task.json`.
- [x] Tạo `tasks/examples/invalid_task.json`.
- [x] Validator chạy bằng `python3 validators/validate_task.py <file>`.
- [x] File hợp lệ in: `✅ Task file hợp lệ`.
- [x] File không hợp lệ in: `❌ Lỗi: <mô tả lỗi cụ thể>`.

### Ghi chú thực tế

- Môi trường ban đầu không có `python3`.
- Đã cài Python 3.11.2 bằng package manager của hệ thống.
- `valid_task.json` pass.
- `invalid_task.json` fail đúng kỳ vọng với lỗi cụ thể: `Field không được phép: unexpected_field`.

## ✅ Bước 3 — Dockerfile LeeJ Agent

### Việc đã làm

- [x] Tạo `docker/Dockerfile`.
- [x] Tạo `.dockerignore`.
- [x] Cập nhật `README.md` với lệnh build/run Docker.
- [x] Build image `openclaw-ai:leej-sprint0` thành công.
- [x] Chạy smoke test container thành công.

### Ghi chú thực tế

- Dockerfile dùng base image `python:3.11-slim`.
- `CMD` tạm thời chạy validator smoke test:
  `python3 validators/validate_task.py tasks/examples/valid_task.json`.
- Lý do: mỗi lần `docker run` là một lần kiểm tra runtime còn sống và schema vẫn hợp lệ.
- Sau Sprint 0 sẽ thay bằng entrypoint thật của LeeJ Agent.

## ✅ Bước 4 — Obsidian vault structure

### Việc đã làm

- [x] Tạo `README.md` trong từng thư mục vault.
- [x] Tạo `vaults/openclaw-ai/00-overview/project.md`.
- [x] Nội dung vault viết bằng tiếng Việt.
- [x] Cấu trúc vault theo tài liệu mục 6.1.

### Cấu trúc Obsidian vault đã có

- [x] `vaults/openclaw-ai/00-overview/`
- [x] `vaults/openclaw-ai/01-tasks/`
- [x] `vaults/openclaw-ai/02-outputs/`
- [x] `vaults/openclaw-ai/03-logs/`
- [x] `vaults/openclaw-ai/04-decisions/`
- [x] `vaults/openclaw-ai/05-retrospective/`

## Output chính của Sprint 0

```text
README.md
.dockerignore
docs/architecture/openclaw_knowledge_base_v2.txt
docs/sprint-0.md
schemas/task.schema.json
validators/validate_task.py
tasks/examples/valid_task.json
tasks/examples/invalid_task.json
docker/Dockerfile
vaults/openclaw-ai/00-overview/README.md
vaults/openclaw-ai/00-overview/project.md
vaults/openclaw-ai/01-tasks/README.md
vaults/openclaw-ai/02-outputs/README.md
vaults/openclaw-ai/03-logs/README.md
vaults/openclaw-ai/04-decisions/README.md
vaults/openclaw-ai/05-retrospective/README.md
```

## Lệnh kiểm tra đã chạy

```bash
python3 validators/validate_task.py tasks/examples/valid_task.json
python3 validators/validate_task.py tasks/examples/invalid_task.json
docker build -f docker/Dockerfile -t openclaw-ai:leej-sprint0 .
docker run --rm openclaw-ai:leej-sprint0
find vaults/ -type f
```

## Kết luận

Sprint 0 đạt mục tiêu: có project scaffold, task schema, validator, Docker smoke test và Obsidian vault tối thiểu để bắt đầu Sprint 1.
