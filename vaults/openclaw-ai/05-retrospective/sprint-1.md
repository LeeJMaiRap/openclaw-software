# Retrospective — Sprint 1

## Những gì đã làm được

- Tạo `leej/leej_agent.py` để nhận yêu cầu user và sinh task JSON hợp lệ.
- Hỗ trợ input qua command argument, stdin và `--file`.
- Sinh `TASK-001` từ yêu cầu: `Viết hàm Python tính số Fibonacci thứ n`.
- Tạo acceptance criteria cụ thể bằng template theo loại task, không dùng câu generic.
- Validate task bằng `validators/validate_task.py`.
- Ghi task log vào Obsidian tại `vaults/openclaw-ai/01-tasks/TASK-001.md`.
- Tạo `leej/dispatcher.py` để đọc task, chọn worker/model, sinh payload cron `agentTurn`.
- Giữ đúng model mapping Sprint 1:
  - `claude-cli → gpt-gmn-token-tunel/cx/gpt-5.3-codex`
  - `codex-cli → gpt-gmn-token-tunel/cx/gpt-5.3-codex-high`
  - `hermes → gpt-gmn-token-tunel/cx/gpt-5.4`
  - `manual → không spawn session`
- Ghi dispatch log vào `vaults/openclaw-ai/03-logs/TASK-001-dispatch.md`.
- Spawn Worker session qua cron tool sau khi dispatcher chuẩn bị payload.
- Ghi Worker output vào `vaults/openclaw-ai/02-outputs/TASK-001-output.md`.
- Ghi completion log vào `vaults/openclaw-ai/03-logs/TASK-001-done.md`.
- Tạo `leej/checker.py` để kiểm tra task output theo acceptance criteria.
- Ghi check log vào `vaults/openclaw-ai/03-logs/TASK-001-check.md`.
- Hoàn thành luồng end-to-end đầu tiên cho TASK-001.

## Vấn đề gặp phải và cách giải quyết

### 1. Memory search không khả dụng

Vấn đề: memory index bị pause vì khác embedding provider/model/settings.

Cách giải quyết:

- Không dựa vào memory search.
- Kiểm tra repo trực tiếp bằng `git status`, `find`, file docs và vault.

Bài học: Sprint 2 nên có checklist repo-local đủ rõ để tiếp tục dù memory index không dùng được.

### 2. Python 3 không tồn tại trong runtime mới

Vấn đề: runtime hiện tại không có `python3`, dù Sprint 0 đã từng cài trong phiên trước.

Cách giải quyết:

- Cài lại Python 3.11.2 bằng package manager.
- Chạy lại script/test.

Bài học: dependency cần được container hóa hoặc check bằng script trước khi chạy Sprint logic.

### 3. Python dispatcher không thể tự gọi cron tool

Vấn đề: không có API/CLI rõ ràng để Python gọi OpenClaw cron tool trực tiếp. Tự bịa command là rủi ro.

Cách giải quyết:

- `dispatcher.py` chỉ đọc task, chọn model, sinh payload và ghi log.
- OpenClaw runtime dùng cron tool thật để spawn agentTurn trong phiên orchestration.

Bài học: Sprint 2 cần thiết kế tool bridge rõ ràng nếu muốn script nội bộ tự dispatch không cần human/assistant runtime can thiệp.

### 4. Model allowlist reject

Vấn đề: cron preflight reject `gpt-gmn-token-tunel/cx/gpt-5.3-codex` vì model chưa nằm trong `agents.defaults.models` allowlist.

Cách giải quyết:

- Thêm các model Sprint 1 vào allowlist:
  - `gpt-gmn-token-tunel/cx/gpt-5.3-codex`
  - `gpt-gmn-token-tunel/cx/gpt-5.3-codex-high`
  - `gpt-gmn-token-tunel/cx/gpt-5.4`
- Thêm provider model entries tương ứng.
- Validate config.
- Restart Docker host/gateway runtime để config apply.

Bài học: model mapping phải đi kèm config validation + runtime apply check trước khi dispatch Worker.

### 5. Gateway không hot reload được qua CLI trong môi trường này

Vấn đề: `openclaw config patch` yêu cầu restart gateway, nhưng `openclaw gateway restart` không restart được do service disabled/runtime unknown.

Cách giải quyết:

- Ghi rõ hạn chế này trong docs.
- Dùng restart Docker host/gateway runtime bên ngoài CLI hiện tại.

Bài học: Sprint 2 cần quy trình vận hành rõ: cấu hình nào hot reload, cấu hình nào cần restart, và cách xác nhận `config applied`.

## Bài học cho Sprint 2

- Thêm `scripts/check_env.sh` hoặc `make smoke` để kiểm tra Python, Docker, config model allowlist, cron khả dụng.
- Tạo `leej/models.py` hoặc config file riêng cho worker→model mapping thay vì hardcode trong dispatcher.
- Tạo `leej/config_check.py` để xác nhận model mapping đều nằm trong OpenClaw allowlist trước khi spawn.
- Thiết kế bridge cho dispatcher gọi OpenClaw cron API/tool một cách chính thức.
- Cải thiện checker: không chỉ string-match acceptance criteria, mà kiểm tra output theo evidence hoặc test command.
- Chuẩn hóa Worker output format để checker dễ đọc hơn.
- Ghi trạng thái task lifecycle rõ: `created`, `dispatched`, `running`, `done`, `checked`, `failed`.
- Thêm retry policy khi Worker spawn fail do config hoặc runtime.
- Container hóa LeeJ Agent script để tránh mất dependency giữa phiên.
