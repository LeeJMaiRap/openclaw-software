# 03-logs

Thư mục này lưu log vận hành của LeeJ Agent, dispatcher, checker, runtime handoff và Worker.

Các loại file chính:

```text
B-xxx-batch.md              # tóm tắt batch
B-xxx-dispatch-plan.json    # dependency waves và worker mapping
B-xxx-runtime-actions.json  # sessions_send contract để spawn workers
B-xxx-pipeline.md           # pipeline report
B-xxx-check.md              # checker result toàn batch
TASK-xxx-dispatch.md        # log dispatch theo task
TASK-xxx-done.md            # Worker done log theo task
```

Quy tắc:

- Log phải đủ để audit lại một batch mà không cần đọc Discord.
- Done log nên liệt kê file đã tạo/sửa và lệnh kiểm chứng.
- Runtime actions phải dùng đường dẫn tuyệt đối dưới `/data/workspace/openclaw-ai/`.
- PR automation chỉ chạy sau khi Worker đã ghi output/done log và checker pass thật sự.
