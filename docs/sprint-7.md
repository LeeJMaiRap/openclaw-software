# Sprint 7 — Discord full: category/channel/thread + lifecycle

## Status

✅ Done — E2E passed on 2026-06-07 07:53 UTC.

## Goal

Move from fixed Discord channels to project-scoped Discord workspace lifecycle.

For each project:

```text
Category: project-name
  #leej       ← coordinator command channel
  #workers    ← dispatch/progress log
  #results    ← pipeline/task result summary
  #artifacts  ← report/files
```

## Checklist

- ✅ Added SQLite mapping store: `discord/store.py`.
- ✅ SQLite uses stdlib `sqlite3`; no new dependency.
- ✅ Store schema supports projects, channels, and tasks.
- ✅ Added Discord channel manager: `discord/channel_manager.py`.
- ✅ `!project create <name>` auto-creates category + 4 channels.
- ✅ Project names sanitized: lowercase, spaces to dashes, special chars removed, max 100 chars.
- ✅ Channel roles created: `leej`, `workers`, `results`, `artifacts`.
- ✅ Mapping persisted in SQLite.
- ✅ `!project list` lists mapped projects.
- ✅ `!project done <name>` archives project.
- ✅ `archive_project` implemented: rename category to `[done] project-name`, lock channels by denying Send Messages.
- ✅ `!run "<request>"` in project `#leej` routes by project mapping.
- ✅ Progress goes to `#workers`.
- ✅ Result summary goes to `#results`.
- ✅ Pipeline report/file attachments go to `#artifacts`.
- ✅ Backward compatibility kept: legacy `!run` in fixed input channel still works.
- ✅ `discord/bridge.log` added to `.gitignore`.
- ✅ `discord/state.sqlite3` added to `.gitignore`.

## Files

```text
.gitignore
discord/store.py
discord/channel_manager.py
discord/bridge.py
```

## SQLite mapping store

Default DB path:

```text
discord/state.sqlite3
```

Override:

```text
DISCORD_STORE_PATH
```

Schema:

```sql
projects(id, name, batch_id, category_id, created_at)
channels(project_id, role, channel_id)
tasks(task_id, batch_id, project_id, thread_id, status)
```

Channel roles:

```text
leej | workers | results | artifacts
```

Core API:

```python
init_db()
create_project()
get_project()
get_project_by_category_id()
get_project_by_channel_id()
list_projects()
get_project_channels()
upsert_task()
get_task()
update_task_status()
```

Smoke test:

```bash
python3 discord/store.py
```

Output:

```text
store smoke test OK
```

## Channel manager

Core API:

```python
sanitize_name(name)
create_project_category(guild, project_name)
get_project_by_channel(channel_id)
archive_project(guild, project_name)
```

Behavior:

- Creates one Discord category per project.
- Creates `#leej`, `#workers`, `#results`, `#artifacts` inside category.
- Does not create duplicate category if project exists in store; returns existing mapping.
- Enforces Discord category channel limit guard: max 50 channels/category.
- Archives by renaming category and locking mapped channels.

## Bridge commands

### Create project

```text
!project create openclaw-demo
```

Expected reply:

```text
✅ Project "openclaw-demo" đã tạo
Category và channels đã sẵn sàng.
```

Creates:

```text
Category: openclaw-demo
  #leej
  #workers
  #results
  #artifacts
```

### List projects

```text
!project list
```

Shows active mapped projects and category/channel ids.

### Run pipeline inside project

In `#leej`:

```text
!run "Xây dựng REST API đơn giản bằng Python
dùng http.server. Có unit test."
```

Routing:

```text
#leej      receives command acknowledgement
#workers   receives progress start/finish
#results   receives pipeline summary
#artifacts receives pipeline report attachment
```

### Archive project

```text
!project done openclaw-demo
```

Behavior:

```text
Category renamed to: [done] openclaw-demo
Mapped channels locked: Send Messages denied for @everyone
```

## E2E evidence

Discord E2E passed on 2026-06-07 07:53 UTC.

Test 1:

```text
!project create openclaw-demo
```

Result:

```text
Category openclaw-demo created with #leej, #workers, #results, #artifacts.
```

Test 2:

```text
!run "Xây dựng REST API đơn giản bằng Python
dùng http.server. Có unit test."
```

Result:

```text
#workers: progress dispatch
#results: ✅ Pipeline complete
#artifacts: file/report attached
```

Batch:

```text
B-008
```

Tasks/model routing:

```text
TASK-026 → gpt-gmn-token-tunel/cx/gpt-5.4
TASK-027 → gpt-gmn-token-tunel/cx/gpt-5.5
TASK-028 → gpt-gmn-token-tunel/cx/gpt-5.5
```

Checker:

```text
✅ TASK-026: 3/3 criteria passed
✅ TASK-027: 4/4 criteria passed
✅ TASK-028: 4/4 criteria passed
✅ Batch B-008: 3/3 tasks passed
```

Unit tests:

```text
python3 -m unittest discover -s tests
.............................
----------------------------------------------------------------------
Ran 29 tests in 0.017s

OK
```

Compile gates:

```bash
python3 -m py_compile discord/store.py
python3 -m py_compile discord/channel_manager.py
python3 -m py_compile discord/bridge.py
```

All pass.

## Notes

- `discord/bridge.log` and `discord/state.sqlite3` are ignored.
- If `bridge.log` was already tracked before `.gitignore`, remove from index before commit.
- Discord bot needs Manage Channels for create/archive.
- Discord bot needs Message Content Intent for text command parsing.
- Auto archive after 7 inactive days remains future scheduled lifecycle work; manual archive command is implemented.

## Sprint 8 candidates

- Add automatic 7-day inactive archive cron.
- Add task threads under `#workers` or per-task thread mapping.
- Add project-specific pipeline context into `leej/run.py`.
- Add process supervisor for Discord bridge.
- Add auth allowlist by guild/channel/user/role.
