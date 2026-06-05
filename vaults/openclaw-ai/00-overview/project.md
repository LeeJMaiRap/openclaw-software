# OpenClaw AI — Tóm tắt dự án

OpenClaw AI là hệ thống đa agent chạy trên Docker Desktop, được thiết kế để tự động thực hiện dự án phần mềm từ A đến Z dựa trên yêu cầu của user.

## Mục tiêu

Tự động hóa quy trình phát triển phần mềm: tiếp nhận yêu cầu, làm rõ mục tiêu, lập kế hoạch, chia task, giao Worker thực thi, kiểm tra kết quả, báo cáo lại user và lưu tri thức dài hạn.

## Thành phần chính

- **LeeJ Agent**: PM Core chạy trong Docker, điều phối toàn bộ quy trình.
- **Worker Layer**: các Worker như Claude CLI, Codex CLI, Hermes hoặc OpenClaw sub-agent để thực thi task.
- **Channel**: Telegram, Discord hoặc CLI để giao tiếp với user.
- **GitHub**: nơi lưu trữ code và dữ liệu làm việc.
- **NotebookLM**: kho tài liệu tham khảo read-only.
- **Obsidian**: bộ nhớ dài hạn read/write cho agent.

## Luồng hoạt động happy path

1. User gửi yêu cầu qua Channel.
2. LeeJ Agent hỏi lại để làm rõ goal, constraint và stakeholder.
3. LeeJ tạo problem statement, hypothesis, PRD, user stories và task file.
4. Task file được giao cho Worker phù hợp.
5. Worker thực thi, tạo output và ghi log.
6. LeeJ kiểm tra acceptance criteria, edge cases và launch checklist.
7. Kết quả, quyết định và bài học được lưu vào Obsidian vault.

## Sprint 0

Sprint 0 tập trung vào nền móng tối thiểu, ưu tiên chạy được trước:

- Tạo cấu trúc thư mục dự án.
- Thiết kế JSON Schema và validator cho task file.
- Viết Dockerfile chạy LeeJ Agent smoke test.
- Thiết lập Obsidian vault theo cấu trúc chuẩn.

## Tiêu chí done của task

LeeJ Agent chỉ đánh dấu task hoàn thành khi:

- Tất cả acceptance criteria được đáp ứng.
- Output file tồn tại tại đường dẫn đã chỉ định.
- Không có lỗi compile hoặc runtime.
- Log đã được ghi vào Obsidian vault của dự án.
