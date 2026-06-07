# Sprint 7 Retrospective

## Summary

Sprint 7 expanded Discord from a fixed-channel MVP into project-scoped Discord workspaces.

Status: ✅ Done
E2E passed: 2026-06-07 07:53 UTC

Core result:

```text
!project create openclaw-demo
→ Discord category + 4 role channels
→ SQLite mapping
→ !run in project #leej
→ progress/results/artifacts routed correctly
```

## What shipped

### SQLite mapping store

File:

```text
discord/store.py
```

Why:

```text
Discord IDs need durable mapping state.
JSON would be fragile; SQLite gives simple durable relational lookups with stdlib only.
```

Tables:

```text
projects(id, name, batch_id, category_id, created_at)
channels(project_id, role, channel_id)
tasks(task_id, batch_id, project_id, thread_id, status)
```

Smoke test passed:

```text
store smoke test OK
```

### Discord channel manager

File:

```text
discord/channel_manager.py
```

Functions:

```python
sanitize_name()
create_project_category()
get_project_by_channel()
archive_project()
```

Important behavior:

- sanitizes names for Discord category/channel safety
- creates project category
- creates `#leej`, `#workers`, `#results`, `#artifacts`
- persists mapping to SQLite
- avoids duplicate project creation by checking store first
- archives project by renaming category and locking mapped channels

### Bridge upgrade

File:

```text
discord/bridge.py
```

New commands:

```text
!project create <name>
!project list
!project done <name>
!run "<request>"
```

Routing:

```text
Project #leej command → detect channel_id → SQLite project mapping
#workers              → progress
#results              → pipeline summary
#artifacts            → pipeline report/file
```

Backward compatibility kept:

```text
Legacy !run in #openclaw-general still uses fixed Sprint 6 input/output channel behavior.
```

### Gitignore cleanup

Added:

```text
discord/bridge.log
discord/state.sqlite3
```

Reason:

- logs should not be committed
- local SQLite runtime state should not be committed

## E2E test

### Test 1 — Project create

User sent in `#openclaw-general`:

```text
!project create openclaw-demo
```

Expected and observed:

```text
Category: openclaw-demo
  #leej
  #workers
  #results
  #artifacts
```

### Test 2 — Run pipeline from project channel

User sent in `#leej` under `openclaw-demo`:

```text
!run "Xây dựng REST API đơn giản bằng Python
dùng http.server. Có unit test."
```

Expected and observed routing:

```text
#workers: progress dispatch
#results: ✅ Pipeline complete
#artifacts: file attachment
```

Batch:

```text
B-008
```

Tasks:

```text
TASK-026 — REST API scope
TASK-027 — http.server implementation
TASK-028 — unit tests
```

Model routing:

```text
TASK-026 → gpt-gmn-token-tunel/cx/gpt-5.4
TASK-027 → gpt-gmn-token-tunel/cx/gpt-5.5
TASK-028 → gpt-gmn-token-tunel/cx/gpt-5.5
```

Checker after filesystem artifact completion:

```text
✅ TASK-026: 3/3 criteria passed
✅ TASK-027: 4/4 criteria passed
✅ TASK-028: 4/4 criteria passed
✅ Batch B-008: 3/3 tasks passed
```

Full tests:

```text
Ran 29 tests in 0.017s
OK
```

## What worked

### SQLite was right scope

No extra dependency, enough structure, easy lookup by project/category/channel/task.

### Project category model feels natural

Discord category gives clean project boundary. Four channels map well to OpenClaw roles:

```text
coordination, worker log, result summary, artifacts
```

### Backward compatibility avoided regressions

Sprint 6 `!run` path remains available. This matters because project routing depends on successful mapping; legacy fixed channel remains a fallback.

### Attachment routing improved UX

Artifacts no longer clutter results. Reports go to `#artifacts`, summaries stay in `#results`.

## Issues / lessons

### `bridge.log` was already modified

Adding it to `.gitignore` stops future untracked noise, but if already tracked/modified, it still appears until removed from index or reset.

Lesson:

```text
Ignore runtime logs before first bridge launch.
```

### Runtime process management still fragile

Manual restart used shell commands in container. Container lacked `pkill`, so process cleanup needed care.

Sprint 8 should add managed lifecycle:

```text
bridge status/start/restart/stop
```

### Auto archive not scheduled yet

Manual `!project done` works. Requirement says auto archive after 7 inactive days; actual scheduled inactive scan remains future work.

Need next:

```text
last_active_at in store
cron/heartbeat archive sweep
```

### Pipeline still not fully project-context aware

Discord routes channels correctly. `leej/run.py` still runs project `openclaw-ai` pipeline internally. Future improvement should pass project context explicitly.

## Decisions

- Use sanitized project name as store key.
- Return existing mapping when project already exists instead of creating duplicate Discord category.
- Keep channels fixed per category: `leej`, `workers`, `results`, `artifacts`.
- Keep command syntax text-based; slash commands deferred.
- Keep SQLite file local and ignored.
- Keep logs ignored.

## Final verdict

Sprint 7 succeeded.

It proves OpenClaw can manage Discord as a project workspace UI:

```text
Discord project creation → durable mapping → role-based routing → pipeline output delivery
```

Next bottleneck is lifecycle hardening, not basic Discord capability.
