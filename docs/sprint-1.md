# Sprint 1 — LeeJ agent, dispatcher, checker, end-to-end flow

## Mục tiêu

Tạo luồng tối thiểu để LeeJ nhận task, dispatch worker, ghi output, kiểm tra acceptance criteria và đóng vòng end-to-end.

## Trạng thái tổng kết

✅ Sprint 1 hoàn thành chính thức lúc 2026-06-06 08:36 UTC.

## Checklist 4 bước

- [x] ✅ Done — Bước 1: Tạo task Sprint 1 `TASK-001` cho bài toán Fibonacci.
- [x] ✅ Done — Bước 2: Tạo LeeJ agent/dispatcher tối thiểu để xử lý task.
- [x] ✅ Done — Bước 3: Worker viết output Fibonacci và log hoàn thành.
- [x] ✅ Done — Bước 4: Tạo `leej/checker.py`, chạy kiểm tra `TASK-001` đạt `3/3 criteria passed`.

## Output chính

- `tasks/TASK-001.json`
- `vaults/openclaw-ai/01-tasks/TASK-001.md`
- `leej/leej_agent.py`
- `leej/dispatcher.py`
- `leej/checker.py`
- `vaults/openclaw-ai/02-outputs/TASK-001-output.md`
- `vaults/openclaw-ai/03-logs/TASK-001-dispatch.md`
- `vaults/openclaw-ai/03-logs/TASK-001-done.md`
- `vaults/openclaw-ai/03-logs/TASK-001-check.md`

## Vấn đề gặp phải

### Model allowlist

Trong quá trình dispatch worker, model bị chặn do allowlist không nhận model đang dùng.

Cách fix:

- Cập nhật cấu hình allowlist phù hợp.
- Restart Docker host để gateway nhận cấu hình mới.

### Gateway không hot reload qua CLI

Trong môi trường này, gateway không hot reload được qua CLI. Thay đổi cấu hình không có hiệu lực ngay nếu chỉ dùng CLI.

Ghi chú:

- Cần restart Docker host khi cần ép gateway nạp lại cấu hình.
- Không giả định hot reload hoạt động trong Sprint 2.

## Lệnh kiểm tra đã chạy

```bash
python3 leej/checker.py tasks/TASK-001.json
```

Kết quả:

```text
✅ TASK-001: 3/3 criteria passed
```

## Kết luận

Sprint 1 đạt mục tiêu: có luồng end-to-end đơn giản từ task JSON tới output, log, checker và kết quả kiểm chứng acceptance criteria.
