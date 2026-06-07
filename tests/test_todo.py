import json
import tempfile
import unittest
from pathlib import Path

from todo import (
    TodoList,
    add_todo,
    delete_todo,
    get_all_todos,
    mark_todo_complete,
    read_todos_from_file,
    save_todos_to_file,
)


class TestTodoList(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.todo_file = Path(self.temp_dir.name) / "todos.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_todo_keeps_item_in_memory_and_file(self):
        todo_list = TodoList(self.todo_file)

        todo = todo_list.add("Mua sữa")

        self.assertEqual(todo["content"], "Mua sữa")
        self.assertFalse(todo["completed"])
        self.assertTrue(todo["id"].startswith("todo-"))
        self.assertEqual(todo_list.get_all(), [todo])
        self.assertEqual(read_todos_from_file(self.todo_file), [todo])

    def test_delete_todo_by_id(self):
        todo_list = TodoList(self.todo_file)
        todo = todo_list.add("Học Python")

        self.assertTrue(todo_list.delete(todo["id"]))
        self.assertEqual(todo_list.get_all(), [])
        self.assertEqual(read_todos_from_file(self.todo_file), [])
        self.assertFalse(todo_list.delete("missing-id"))

    def test_mark_existing_todo_complete(self):
        todo_list = TodoList(self.todo_file)
        todo = todo_list.add("Viết test")

        updated = todo_list.mark_complete(todo["id"])

        self.assertIsNotNone(updated)
        self.assertTrue(updated["completed"])
        self.assertEqual(read_todos_from_file(self.todo_file)[0]["completed"], True)
        self.assertIsNone(todo_list.mark_complete("missing-id"))

    def test_save_todos_writes_expected_json_structure(self):
        todos = [
            {"id": "todo-001", "content": "Mua sữa", "completed": False},
            {"id": "todo-002", "content": "Học Node.js", "completed": True},
        ]

        save_todos_to_file(todos, self.todo_file)

        raw = json.loads(self.todo_file.read_text(encoding="utf-8"))
        self.assertIsInstance(raw, list)
        self.assertEqual(raw, todos)
        self.assertEqual(set(raw[0].keys()), {"id", "content", "completed"})

    def test_read_todos_restores_list_from_json_file(self):
        todos = [
            {"id": "todo-001", "content": "Mua sữa", "completed": False},
            {"id": "todo-002", "content": "Học Node.js", "completed": True},
        ]
        self.todo_file.write_text(json.dumps(todos, ensure_ascii=False), encoding="utf-8")

        self.assertEqual(read_todos_from_file(self.todo_file), todos)
        self.assertEqual(TodoList(self.todo_file).get_all(), todos)

    def test_read_missing_or_empty_file_returns_empty_list(self):
        self.assertEqual(read_todos_from_file(self.todo_file), [])
        self.todo_file.write_text("", encoding="utf-8")
        self.assertEqual(read_todos_from_file(self.todo_file), [])

    def test_function_api(self):
        todo = add_todo("Dọn bàn", self.todo_file)

        self.assertEqual(get_all_todos(self.todo_file), [todo])
        self.assertTrue(mark_todo_complete(todo["id"], self.todo_file)["completed"])
        self.assertTrue(delete_todo(todo["id"], self.todo_file))
        self.assertEqual(get_all_todos(self.todo_file), [])


if __name__ == "__main__":
    unittest.main()
