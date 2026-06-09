# Sprint 11 Retrospective — Persistent worker sessions + sessions_send dispatch

## Status

✅ Done — 2026-06-09 01:43 UTC.

## What shipped

Sprint 11 changed OpenClaw AI from per-task temporary cron sessions toward project-scoped persistent worker sessions.

Each Discord project now has:

```text
#leej
#workers
#results
#artifacts
#worker-code
#worker-hermes
#worker-test
```

and SQLite worker rows:

```text
worker-code   → agent:software:project-<id>-worker-code
worker-hermes → agent:software:project-<id>-worker-hermes
worker-test   → agent:software:project-<id>-worker-test
```

LeeJ dispatcher now emits `sessions_send` payloads for project runs instead of cron jobs per task.

## Key validation

Project:

```text
sprint11-test-3
project_id=5
```

Worker session send test:

```text
sessions_send sessionKey=agent:software:project-5-worker-code
reply="Nhận được."
```

B-010 request:

```text
Viết hàm Python tính tổng các số chẵn trong một danh sách. Có unit test.
```

B-010 runtime actions:

```text
TASK-032 → agent:software:project-5-worker-hermes → sessions_send
TASK-033 → agent:software:project-5-worker-code   → sessions_send
TASK-034 → agent:software:project-5-worker-code   → sessions_send
```

Result:

```text
B-010 pass with sessions_send dispatch.
```

## Important decisions

### Correct session visibility config

Correct path:

```text
tools.sessions.visibility = agent
```

Wrong path:

```text
agents.defaults.tools.sessions.visibility
```

Lesson: config schema path matters. Root `tools.sessions.visibility` controls session tool visibility.

### Correct worker session key format

Use:

```text
agent:software:project-<id>-worker-<role>
```

Examples:

```text
agent:software:project-5-worker-code
agent:software:project-5-worker-hermes
agent:software:project-5-worker-test
```

### sessions_send over cron per task

Cron CLI `--session-key` alone was not enough for reliable persistent named session targeting. Real tool target format for cron-created named sessions is:

```text
session:agent:software:<key>
```

But once `tools.sessions.visibility=agent` was set, direct `sessions_send` to persistent worker sessions became the clean path.

## What went well

- Store model stayed simple: SQLite maps project → worker → channel/session key.
- Persistent worker session concept tested with real OpenClaw sessions, not fake assumptions.
- Visibility issue was diagnosed from schema and verified with an actual `sessions_send` success.
- B-010 proved dispatcher can generate project-scoped sessions_send runtime actions.

## What hurt

- `sessions_spawn(mode="session")` was not available in current runtime tool schema.
- CLI cron behavior with `--session-key` looked promising but actually created isolated run sessions.
- Wrong config path crashed gateway once.
- Discord REST still returned 403 earlier, requiring manual Discord messages for some tests.

## Follow-ups

- Implement runtime executor that actually consumes `B-xxx-runtime-actions.json` and calls `sessions_send` per wave automatically.
- Have LeeJ mediate worker results, run checker, and post summarized status to `#results`.
- Add branch/commit/push/PR workflow after checker pass.
- Archive broken old test projects:
  ```text
  sprint11-test
  sprint11-test-2
  ```
- Rotate exposed Discord Bot Token.

## Verification

Commands used during closeout:

```bash
python3 -m py_compile discord/bridge.py leej/dispatcher.py leej/run.py
python3 discord/store.py
```

Expected output:

```text
store smoke test OK
```
