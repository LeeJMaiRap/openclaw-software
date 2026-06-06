# Sprint 1 — LeeJ Agent: nhận yêu cầu → sinh task → giao Worker đúng model

## Trạng thái tổng kết

✅ Sprint 1 hoàn thành chính thức lúc Sat 2026-06-06 08:41 UTC.

## Mục tiêu

Xây luồng đầu tiên chạy được end-to-end:

```text
user input → LeeJ sinh task file → dispatcher giao Worker đúng model → Worker thực thi → ghi output về Obsidian → LeeJ kiểm tra và báo cáo
```

## ✅ Bước 1 — LeeJ Agent script

### Output

- [x] Tạo `leej/leej_agent.py`.
- [x] Nhận input từ command argument, stdin hoặc `--file`.
- [x] Sinh task file hợp lệ theo `schemas/task.schema.json`.
- [x] Validate task bằng `validators/validate_task.py`.
- [x] Lưu task vào `tasks/TASK-001.json`.
- [x] Ghi log task vào `vaults/openclaw-ai/01-tasks/TASK-001.md`.

### Test đã chạy

```bash
python3 leej/leej_agent.py "Viết hàm Python tính số Fibonacci thứ n"
python3 validators/validate_task.py tasks/TASK-001.json
```

Kết quả:

```text
✅ Task TASK-001 đã tạo: tasks/TASK-001.json
✅ Task file hợp lệ
```

## ✅ Bước 2 — Worker Dispatcher

### Output

- [x] Tạo `leej/dispatcher.py`.
- [x] Đọc `tasks/TASK-001.json`.
- [x] Chọn model theo worker mapping.
- [x] Sinh payload JSON chuẩn cho cron `agentTurn`.
- [x] Ghi log dispatch vào `vaults/openclaw-ai/03-logs/TASK-001-dispatch.md`.
- [x] Spawn session bằng cron tool.

### Mapping giữ nguyên

```text
claude-cli → gpt-gmn-token-tunel/cx/gpt-5.3-codex
codex-cli  → gpt-gmn-token-tunel/cx/gpt-5.3-codex-high
hermes     → gpt-gmn-token-tunel/cx/gpt-5.4
manual     → không spawn session
```

### Ghi chú thực tế

- `dispatcher.py` không gọi cron trực tiếp vì chưa có CLI/API nội bộ an toàn để gọi từ Python.
- Dispatcher chuẩn bị payload + ghi log.
- OpenClaw runtime dùng cron tool để spawn thật trong phiên chạy.

## ✅ Bước 3 — Worker output + Obsidian

### Output

- [x] Worker session hoàn thành.
- [x] Ghi output vào `vaults/openclaw-ai/02-outputs/TASK-001-output.md`.
- [x] Ghi log hoàn thành vào `vaults/openclaw-ai/03-logs/TASK-001-done.md`.

### Ghi chú thực tế

- Cron job đầu tiên bị lỗi do model chưa nằm trong allowlist.
- Sau khi cập nhật allowlist và restart Docker host/gateway runtime, Worker chạy được.

## ✅ Bước 4 — LeeJ kiểm tra và báo cáo

### Output

- [x] Tạo `leej/checker.py`.
- [x] Đọc task file và output file.
- [x] Kiểm tra acceptance criteria.
- [x] Ghi log check vào `vaults/openclaw-ai/03-logs/TASK-001-check.md`.

### Kỳ vọng báo cáo

```text
✅ TASK-001: 3/3 criteria passed
```

## Vấn đề thực tế

### 1. Model allowlist reject

Cron preflight ban đầu reject model:

```text
gpt-gmn-token-tunel/cx/gpt-5.3-codex
```

Lý do: `agents.defaults.models` chưa allow 3 model Sprint 1.

Cách fix:

- Thêm 3 model vào config allowlist:
  - `gpt-gmn-token-tunel/cx/gpt-5.3-codex`
  - `gpt-gmn-token-tunel/cx/gpt-5.3-codex-high`
  - `gpt-gmn-token-tunel/cx/gpt-5.4`
- Thêm model provider entries tương ứng.
- Validate config.
- Restart Docker host/gateway runtime để config thật sự apply.

### 2. Gateway không hot reload được qua CLI trong môi trường này

`openclaw config patch` báo:

```text
Restart the gateway to apply.
```

`openclaw gateway restart` không restart được service trong runtime này vì:

```text
Gateway service disabled.
Runtime: unknown (systemctl not available; systemd user services are required on Linux.)
```

Cách xử lý thực tế: restart Docker host/gateway runtime bên ngoài CLI hiện tại.

## Kết luận

Sprint 1 đạt mục tiêu: đã có LeeJ Agent tạo task, dispatcher chọn đúng model, Worker chạy qua OpenClaw session, output ghi về Obsidian, checker kiểm tra kết quả.
