# 01-tasks

Thư mục này lưu bản mô tả task dạng Markdown do LeeJ Agent tạo ra để giao cho Worker.

Mỗi task nên có:

- Task ID
- batch ID
- mục tiêu rõ ràng
- acceptance criteria đo được
- dependency nếu có
- worker/role phụ trách
- constraint và timeout
- đường dẫn output/done-log tuyệt đối mà Worker phải ghi

Task nguồn dạng JSON nằm trong `/tasks/*.json`. Thư mục này là bản dễ đọc trong vault để review, audit và điều phối thủ công khi cần.
