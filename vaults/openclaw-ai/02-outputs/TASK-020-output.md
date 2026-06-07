# TASK-020 — Cấu trúc dữ liệu todo, API module, quy tắc lưu/đọc JSON

## 1. Cấu trúc dữ liệu todo
Giữ đơn giản cho Sprint 5. Mỗi todo item nên có:

```json
{
  "id": "todo-001",
  "content": "Mua sữa",
  "completed": false
}
```

### Trường bắt buộc
- `id`: `string`
  - Định danh duy nhất cho todo
  - Có thể dùng timestamp hoặc UUID đơn giản
- `content`: `string`
  - Nội dung công việc
  - Không nên để rỗng
- `completed`: `boolean`
  - `true`: đã hoàn thành
  - `false`: chưa hoàn thành

## 2. API module cần có
Có thể gom trong `todoService` hoặc `todoRepository` đơn giản.

### Hàm xử lý nghiệp vụ
1. `addTodo(content: string): Todo`
   - Tạo todo mới
   - Sinh `id`
   - Gán `completed = false`
   - Lưu lại file JSON

2. `deleteTodo(id: string): boolean`
   - Xóa todo theo `id`
   - Trả `true` nếu xóa thành công
   - Trả `false` nếu không tìm thấy
   - Lưu lại file JSON sau khi xóa

3. `toggleTodoComplete(id: string): Todo | null`
   - Đổi trạng thái `completed`
   - `false -> true` hoặc `true -> false`
   - Trả todo đã cập nhật
   - Trả `null` nếu không tìm thấy
   - Lưu lại file JSON sau khi cập nhật

> Nếu bài toán chỉ cần “đánh dấu hoàn thành”, có thể dùng:
- `markTodoComplete(id: string): Todo | null`
  - Chỉ gán `completed = true`

### Hàm đọc/ghi file
4. `readTodosFromFile(): Todo[]`
   - Đọc file JSON
   - Parse dữ liệu thành mảng todo
   - Nếu file chưa tồn tại hoặc rỗng thì trả `[]`

5. `saveTodosToFile(todos: Todo[]): void`
   - Ghi toàn bộ mảng todo xuống file JSON
   - Ghi đè nội dung cũ

### Hàm hỗ trợ nên có
6. `getAllTodos(): Todo[]`
   - Trả toàn bộ danh sách todo
   - Dùng cho hiển thị hoặc debug

## 3. Định dạng file JSON đầu ra
Nên lưu dưới dạng mảng object JSON:

```json
[
  {
    "id": "todo-001",
    "content": "Mua sữa",
    "completed": false
  },
  {
    "id": "todo-002",
    "content": "Học Node.js",
    "completed": true
  }
]
```

## 4. Quy tắc lưu/đọc file JSON

### Khi đọc file
- Nếu file **chưa tồn tại**:
  - Tạo logic mặc định trả về mảng rỗng `[]`
  - Không báo lỗi cho luồng chính
- Nếu file **tồn tại nhưng rỗng**:
  - Xem như chưa có dữ liệu
  - Trả về `[]`
- Nếu file có dữ liệu hợp lệ:
  - Parse JSON
  - Kiểm tra kết quả là mảng
- Nếu file lỗi format JSON:
  - Nên báo lỗi rõ ràng để dễ debug
  - Sprint 5 có thể cho phép ném lỗi trực tiếp

### Khi lưu file
- Luôn ghi toàn bộ danh sách todo hiện tại
- Dùng `JSON.stringify(todos, null, 2)` để dễ đọc
- Ghi đè file cũ sau mỗi thao tác thêm, xóa, đánh dấu hoàn thành

## 5. Gợi ý kiểu dữ liệu
```ts
type Todo = {
  id: string;
  content: string;
  completed: boolean;
};
```

## 6. Kết luận ngắn
Thiết kế tối giản cho Sprint 5:
- Dữ liệu todo: `id`, `content`, `completed`
- API chính: `addTodo`, `deleteTodo`, `toggleTodoComplete` hoặc `markTodoComplete`
- File JSON: lưu mảng todo
- File chưa tồn tại hoặc rỗng: trả `[]`

## Verification notes
- Đã mô tả đủ trường tối thiểu: `id`, `content`, `completed`
- Đã liệt kê hàm thêm, xóa, đánh dấu hoàn thành, đọc file, lưu file
- Đã nêu rõ định dạng JSON và xử lý file chưa tồn tại/rỗng
