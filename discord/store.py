from __future__ import annotations

import os
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROLE_NAMES = {"leej", "workers", "results", "artifacts"}
WORKER_STATUSES = {"active", "done", "archived"}
DEFAULT_DB_PATH = Path(__file__).with_name("state.sqlite3")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def resolve_db_path(path: Path | str | None = None) -> Path | str:
    if path is not None:
        return Path(path) if path != ":memory:" else ":memory:"
    env_path = os.environ.get("DISCORD_STORE_PATH")
    if env_path:
        return Path(env_path) if env_path != ":memory:" else ":memory:"
    return DEFAULT_DB_PATH


def connect(path: Path | str | None = None) -> sqlite3.Connection:
    db_path = resolve_db_path(path)
    if isinstance(db_path, Path):
        db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(path: Path | str | None = None) -> Path | str:
    db_path = resolve_db_path(path)
    with connect(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                batch_id TEXT,
                category_id TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS channels (
                project_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('leej', 'workers', 'results', 'artifacts')),
                channel_id TEXT NOT NULL,
                PRIMARY KEY(project_id, role),
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                batch_id TEXT NOT NULL,
                project_id INTEGER NOT NULL,
                thread_id TEXT,
                status TEXT NOT NULL,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS workers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                channel_id TEXT NOT NULL UNIQUE,
                session_key TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('active', 'done', 'archived')),
                created_at TEXT NOT NULL,
                last_active_at TEXT NOT NULL,
                UNIQUE(project_id, name),
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );
            """
        )
    return db_path

def validate_worker_status(status: str) -> None:
    if status not in WORKER_STATUSES:
        raise ValueError(f"invalid worker status: {status}")


def validate_channels(channels: dict[str, str]) -> None:
    missing = ROLE_NAMES - set(channels)
    extra = set(channels) - ROLE_NAMES
    if missing:
        raise ValueError(f"missing channel roles: {', '.join(sorted(missing))}")
    if extra:
        raise ValueError(f"unknown channel roles: {', '.join(sorted(extra))}")
    for role, channel_id in channels.items():
        if not str(channel_id).strip():
            raise ValueError(f"empty channel_id for role: {role}")


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return dict(row)


def create_project(
    name: str,
    category_id: str,
    channels: dict[str, str],
    batch_id: str | None = None,
    path: Path | str | None = None,
) -> int:
    name = name.strip()
    if not name:
        raise ValueError("project name is required")
    if not str(category_id).strip():
        raise ValueError("category_id is required")
    validate_channels(channels)
    init_db(path)

    with connect(path) as conn:
        cur = conn.execute(
            """
            INSERT INTO projects(name, batch_id, category_id, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (name, batch_id, str(category_id), utc_now()),
        )
        project_id = int(cur.lastrowid)
        conn.executemany(
            """
            INSERT INTO channels(project_id, role, channel_id)
            VALUES (?, ?, ?)
            """,
            [(project_id, role, str(channel_id)) for role, channel_id in channels.items()],
        )
    return project_id


def get_project(name: str, path: Path | str | None = None) -> dict[str, Any] | None:
    init_db(path)
    with connect(path) as conn:
        row = conn.execute(
            "SELECT id, name, batch_id, category_id, created_at FROM projects WHERE name = ?",
            (name,),
        ).fetchone()
    return row_to_dict(row)


def get_project_by_category_id(category_id: str, path: Path | str | None = None) -> dict[str, Any] | None:
    init_db(path)
    with connect(path) as conn:
        row = conn.execute(
            "SELECT id, name, batch_id, category_id, created_at FROM projects WHERE category_id = ?",
            (str(category_id),),
        ).fetchone()
    return row_to_dict(row)

def update_project_batch_id(project_id: int, batch_id: str, path: Path | str | None = None) -> None:
    if not batch_id.strip():
        raise ValueError("batch_id is required")
    init_db(path)
    with connect(path) as conn:
        cur = conn.execute(
            "UPDATE projects SET batch_id = ? WHERE id = ?",
            (batch_id.strip(), int(project_id)),
        )
        if cur.rowcount == 0:
            raise KeyError(f"project not found: {project_id}")


def list_projects(path: Path | str | None = None) -> list[dict[str, Any]]:
    init_db(path)
    with connect(path) as conn:
        rows = conn.execute(
            "SELECT id, name, batch_id, category_id, created_at FROM projects ORDER BY created_at, id"
        ).fetchall()
    return [dict(row) for row in rows]


def get_project_channels(project: int | str, path: Path | str | None = None) -> dict[str, str]:
    init_db(path)
    with connect(path) as conn:
        if isinstance(project, int) or str(project).isdigit():
            where_clause = "p.id = ?"
            value: int | str = int(project)
        else:
            where_clause = "p.name = ?"
            value = str(project)
        rows = conn.execute(
            f"""
            SELECT c.role, c.channel_id
            FROM channels c
            JOIN projects p ON p.id = c.project_id
            WHERE {where_clause}
            ORDER BY c.role
            """,
            (value,),
        ).fetchall()
    return {str(row["role"]): str(row["channel_id"]) for row in rows}




def get_project_by_channel_id(channel_id: str, path: Path | str | None = None) -> dict[str, Any] | None:
    init_db(path)
    with connect(path) as conn:
        row = conn.execute(
            """
            SELECT p.id, p.name, p.batch_id, p.category_id, p.created_at, c.role, c.channel_id
            FROM channels c
            JOIN projects p ON p.id = c.project_id
            WHERE c.channel_id = ?
            """,
            (str(channel_id),),
        ).fetchone()
    return row_to_dict(row)

def create_worker(
    project_id: int,
    name: str,
    channel_id: str,
    session_key: str,
    path: Path | str | None = None,
) -> int:
    name = name.strip()
    channel_id = str(channel_id).strip()
    session_key = session_key.strip()
    if not name:
        raise ValueError("worker name is required")
    if not channel_id:
        raise ValueError("worker channel_id is required")
    if not session_key:
        raise ValueError("worker session_key is required")
    init_db(path)

    now = utc_now()
    with connect(path) as conn:
        project = conn.execute("SELECT id FROM projects WHERE id = ?", (int(project_id),)).fetchone()
        if project is None:
            raise KeyError(f"project not found: {project_id}")
        cur = conn.execute(
            """
            INSERT INTO workers(project_id, name, channel_id, session_key, status, created_at, last_active_at)
            VALUES (?, ?, ?, ?, 'active', ?, ?)
            """,
            (int(project_id), name, channel_id, session_key, now, now),
        )
        return int(cur.lastrowid)

def get_worker(name: str, project_id: int, path: Path | str | None = None) -> dict[str, Any] | None:
    init_db(path)
    with connect(path) as conn:
        row = conn.execute(
            """
            SELECT id, project_id, name, channel_id, session_key, status, created_at, last_active_at
            FROM workers
            WHERE project_id = ? AND name = ?
            """,
            (int(project_id), name),
        ).fetchone()
    return row_to_dict(row)

def get_worker_by_channel(channel_id: str, path: Path | str | None = None) -> dict[str, Any] | None:
    init_db(path)
    with connect(path) as conn:
        row = conn.execute(
            """
            SELECT id, project_id, name, channel_id, session_key, status, created_at, last_active_at
            FROM workers
            WHERE channel_id = ?
            """,
            (str(channel_id),),
        ).fetchone()
    return row_to_dict(row)

def update_worker_status(name: str, project_id: int, status: str, path: Path | str | None = None) -> None:
    validate_worker_status(status)
    init_db(path)
    with connect(path) as conn:
        cur = conn.execute(
            """
            UPDATE workers
            SET status = ?, last_active_at = ?
            WHERE project_id = ? AND name = ?
            """,
            (status, utc_now(), int(project_id), name),
        )
        if cur.rowcount == 0:
            raise KeyError(f"worker not found: {name}")

def list_workers(project_id: int, path: Path | str | None = None) -> list[dict[str, Any]]:
    init_db(path)
    with connect(path) as conn:
        rows = conn.execute(
            """
            SELECT id, project_id, name, channel_id, session_key, status, created_at, last_active_at
            FROM workers
            WHERE project_id = ?
            ORDER BY id
            """,
            (int(project_id),),
        ).fetchall()
    return [dict(row) for row in rows]


def upsert_task(
    task_id: str,
    batch_id: str,
    project_name: str,
    status: str,
    thread_id: str | None = None,
    path: Path | str | None = None,
) -> None:
    if not task_id.strip():
        raise ValueError("task_id is required")
    if not batch_id.strip():
        raise ValueError("batch_id is required")
    if not status.strip():
        raise ValueError("status is required")
    init_db(path)

    with connect(path) as conn:
        project = conn.execute("SELECT id FROM projects WHERE name = ?", (project_name,)).fetchone()
        if project is None:
            raise KeyError(f"project not found: {project_name}")
        conn.execute(
            """
            INSERT INTO tasks(task_id, batch_id, project_id, thread_id, status)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(task_id) DO UPDATE SET
                batch_id = excluded.batch_id,
                project_id = excluded.project_id,
                thread_id = excluded.thread_id,
                status = excluded.status
            """,
            (task_id, batch_id, int(project["id"]), thread_id, status),
        )


def get_task(task_id: str, path: Path | str | None = None) -> dict[str, Any] | None:
    init_db(path)
    with connect(path) as conn:
        row = conn.execute(
            """
            SELECT t.task_id, t.batch_id, p.name AS project_name, p.id AS project_id,
                   t.thread_id, t.status
            FROM tasks t
            JOIN projects p ON p.id = t.project_id
            WHERE t.task_id = ?
            """,
            (task_id,),
        ).fetchone()
    return row_to_dict(row)

def list_tasks_by_project(project_id: int, path: Path | str | None = None) -> list[dict[str, Any]]:
    init_db(path)
    with connect(path) as conn:
        rows = conn.execute(
            """
            SELECT t.task_id, t.batch_id, p.name AS project_name, p.id AS project_id,
                   t.thread_id, t.status
            FROM tasks t
            JOIN projects p ON p.id = t.project_id
            WHERE p.id = ?
            ORDER BY t.task_id
            """,
            (int(project_id),),
        ).fetchall()
    return [dict(row) for row in rows]


def update_task_status(task_id: str, status: str, path: Path | str | None = None) -> None:
    if not status.strip():
        raise ValueError("status is required")
    init_db(path)
    with connect(path) as conn:
        cur = conn.execute("UPDATE tasks SET status = ? WHERE task_id = ?", (status, task_id))
        if cur.rowcount == 0:
            raise KeyError(f"task not found: {task_id}")


def smoke_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "store-smoke.sqlite3"
        init_db(db_path)
        project_id = create_project(
            "smoke-project",
            "category-1",
            {
                "leej": "channel-leej",
                "workers": "channel-workers",
                "results": "channel-results",
                "artifacts": "channel-artifacts",
            },
            batch_id="B-SMOKE",
            path=db_path,
        )
        assert project_id > 0

        project = get_project("smoke-project", db_path)
        assert project is not None
        assert project["name"] == "smoke-project"
        assert project["batch_id"] == "B-SMOKE"
        assert project["category_id"] == "category-1"

        projects = list_projects(db_path)
        assert len(projects) == 1

        channels = get_project_channels("smoke-project", db_path)
        assert channels == {
            "leej": "channel-leej",
            "workers": "channel-workers",
            "results": "channel-results",
            "artifacts": "channel-artifacts",
        }

        by_category = get_project_by_category_id("category-1", db_path)
        assert by_category is not None
        assert by_category["name"] == "smoke-project"

        worker_code_id = create_worker(
            project_id,
            "worker-code",
            "channel-worker-code",
            f"project-{project_id}-worker-code",
            db_path,
        )
        worker_hermes_id = create_worker(
            project_id,
            "worker-hermes",
            "channel-worker-hermes",
            f"project-{project_id}-worker-hermes",
            db_path,
        )
        worker_test_id = create_worker(
            project_id,
            "worker-test",
            "channel-worker-test",
            f"project-{project_id}-worker-test",
            db_path,
        )
        assert worker_code_id > 0
        assert worker_hermes_id > 0
        assert worker_test_id > 0

        worker = get_worker("worker-code", project_id, db_path)
        assert worker is not None
        assert worker["name"] == "worker-code"
        assert worker["channel_id"] == "channel-worker-code"
        assert worker["session_key"] == f"project-{project_id}-worker-code"
        assert worker["status"] == "active"

        by_worker_channel = get_worker_by_channel("channel-worker-test", db_path)
        assert by_worker_channel is not None
        assert by_worker_channel["name"] == "worker-test"

        workers = list_workers(project_id, db_path)
        assert [worker["name"] for worker in workers] == [
            "worker-code",
            "worker-hermes",
            "worker-test",
        ]

        update_worker_status("worker-code", project_id, "done", db_path)
        worker = get_worker("worker-code", project_id, db_path)
        assert worker is not None
        assert worker["status"] == "done"

        upsert_task("TASK-SMOKE", "B-SMOKE", "smoke-project", "queued", "thread-1", db_path)
        task = get_task("TASK-SMOKE", db_path)
        assert task is not None
        assert task["task_id"] == "TASK-SMOKE"
        assert task["batch_id"] == "B-SMOKE"
        assert task["project_name"] == "smoke-project"
        assert task["thread_id"] == "thread-1"
        assert task["status"] == "queued"

        update_task_status("TASK-SMOKE", "done", db_path)
        task = get_task("TASK-SMOKE", db_path)
        assert task is not None
        assert task["status"] == "done"

    print("store smoke test OK")


if __name__ == "__main__":
    smoke_test()
