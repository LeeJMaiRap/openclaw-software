"""Simple todo list module with JSON persistence."""

import json
import time
from pathlib import Path

DEFAULT_TODO_FILE = Path("todos.json")


def _new_todo_id():
    """Create a simple unique todo id for Sprint 5."""
    return f"todo-{time.time_ns()}"


class TodoList:
    """Manage todos in memory and persist them to a JSON file."""

    def __init__(self, file_path=DEFAULT_TODO_FILE):
        self.file_path = Path(file_path)
        self.todos = self.read_from_file()

    def get_all(self):
        """Return all todos currently in memory."""
        return list(self.todos)

    def add(self, content):
        """Add a new todo, save it, and return the created item."""
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Todo content must not be empty")

        todo = {
            "id": _new_todo_id(),
            "content": content.strip(),
            "completed": False,
        }
        self.todos.append(todo)
        self.save_to_file()
        return todo

    def delete(self, todo_id):
        """Delete todo by id. Return True if deleted, otherwise False."""
        original_count = len(self.todos)
        self.todos = [todo for todo in self.todos if todo.get("id") != todo_id]

        if len(self.todos) == original_count:
            return False

        self.save_to_file()
        return True

    def mark_complete(self, todo_id):
        """Mark an existing todo as completed. Return updated todo or None."""
        for todo in self.todos:
            if todo.get("id") == todo_id:
                todo["completed"] = True
                self.save_to_file()
                return todo
        return None

    def save_to_file(self):
        """Write current todo list to JSON file."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.write_text(
            json.dumps(self.todos, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def read_from_file(self):
        """Read todo list from JSON file. Missing or empty file returns []."""
        if not self.file_path.exists():
            return []

        content = self.file_path.read_text(encoding="utf-8").strip()
        if not content:
            return []

        data = json.loads(content)
        if not isinstance(data, list):
            raise ValueError("Todo JSON file must contain a list")
        return data


def read_todos_from_file(file_path=DEFAULT_TODO_FILE):
    """Read todos from a JSON file."""
    return TodoList(file_path).get_all()


def save_todos_to_file(todos, file_path=DEFAULT_TODO_FILE):
    """Save todos to a JSON file."""
    todo_list = TodoList(file_path)
    todo_list.todos = list(todos)
    todo_list.save_to_file()


def get_all_todos(file_path=DEFAULT_TODO_FILE):
    """Return all todos from storage."""
    return read_todos_from_file(file_path)


def add_todo(content, file_path=DEFAULT_TODO_FILE):
    """Add a todo to storage and return it."""
    return TodoList(file_path).add(content)


def delete_todo(todo_id, file_path=DEFAULT_TODO_FILE):
    """Delete a todo from storage by id."""
    return TodoList(file_path).delete(todo_id)


def mark_todo_complete(todo_id, file_path=DEFAULT_TODO_FILE):
    """Mark a todo complete by id."""
    return TodoList(file_path).mark_complete(todo_id)
