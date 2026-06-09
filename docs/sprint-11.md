# Sprint 11 — Persistent worker sessions + sessions_send dispatch

## Status

✅ Done — closed on 2026-06-09 01:43 UTC.

## Goal

Make each Discord project own persistent OpenClaw worker sessions and route LeeJ work to those sessions with `sessions_send` instead of one cron job per task.

Target flow:

```text
User in project #leej
→ Discord bridge
→ LeeJ pipeline
→ dispatcher builds sessions_send payloads
→ persistent worker session handles task
→ results/artifacts return to project channels
```

## Checklist

- ✅ Added SQLite `workers` table state for project workers.
- ✅ Created 3 worker channels per Discord project:
  ```text
  #worker-code
  #worker-hermes
  #worker-test
  ```
- ✅ Created 3 worker session records per project.
- ✅ Bootstrapped persistent worker sessions when project is created.
- ✅ Fixed worker session key format:
  ```text
  agent:software:project-<id>-worker-<role>
  ```
- ✅ Confirmed correct target format for named sessions:
  ```text
  session:agent:software:<key>
  ```
- ✅ Fixed session visibility with root config path:
  ```text
  tools.sessions.visibility = agent
  ```
- ✅ Confirmed wrong path is unsafe/wrong:
  ```text
  agents.defaults.tools.sessions.visibility
  ```
- ✅ Verified `sessions_send` into persistent worker session works.
- ✅ Upgraded dispatcher contract from cron-per-task to `sessions_send` when project id is available.
- ✅ Kept cron payload fallback for non-project/legacy mode.
- ✅ Bridge passes project id to pipeline with:
  ```text
  OPENCLAW_DISCORD_PROJECT_ID=<project_id>
  ```
- ✅ B-010 passed with `sessions_send` dispatch.

## SQLite worker state

New worker state lives in SQLite next to project/channel mappings.

Each project gets 3 worker rows:

```text
worker-code
worker-hermes
worker-test
```

Verified for `sprint11-test-3`:

```text
project: {'id': 5, 'name': 'sprint11-test-3', 'batch_id': None, 'category_id': '1513715005235662958', 'created_at': '2026-06-09T01:22:53+00:00'}
worker: worker-code session_key=agent:software:project-5-worker-code
worker: worker-hermes session_key=agent:software:project-5-worker-hermes
worker: worker-test session_key=agent:software:project-5-worker-test
```

## Session visibility

OpenClaw session tool visibility initially blocked cross-session dispatch:

```text
tools.sessions.visibility = tree
```

`tool.sessions_send` returned forbidden for worker sessions outside current tree.

Correct config path:

```text
tools.sessions.visibility = agent
```

Important: this is the root path. Do not set:

```text
agents.defaults.tools.sessions.visibility
```

That path is wrong and previously caused gateway config failure.

Decision:

```text
Use tools.sessions.visibility = agent for Sprint 11 dev.
```

Risk:

```text
agent visibility exposes sessions under same agent id. OK for dev project worker routing; not safe as a broad shared/public default without review.
```

## Session key format

Final reusable worker session key format:

```text
agent:software:project-<project_id>-worker-<role>
```

Examples:

```text
agent:software:project-5-worker-code
agent:software:project-5-worker-hermes
agent:software:project-5-worker-test
```

Worker sessions persist for the Discord project lifecycle.

## sessions_send replaces cron per task

Old task dispatch used cron payloads like:

```json
{
  "sessionTarget": "session:worker-TASK-033",
  "payload": {
    "kind": "agentTurn",
    "message": "..."
  }
}
```

Sprint 11 project dispatch uses `sessions_send` contract:

```json
{
  "dispatchMethod": "sessions_send",
  "sessionKey": "agent:software:project-5-worker-code",
  "payload": {
    "sessionKey": "agent:software:project-5-worker-code",
    "message": "...",
    "timeoutSeconds": 1200
  }
}
```

Fallback remains:

```text
If no OPENCLAW_DISCORD_PROJECT_ID is present, dispatcher keeps cron payload behavior.
```

## Worker mapping

Dispatcher maps logical workers to persistent project workers:

```text
claude-cli → worker-code
codex-cli  → worker-code
hermes     → worker-hermes
```

Worker model map:

```text
worker-code   → gpt-gmn-token-tunel/cx/gpt-5.5
worker-hermes → gpt-gmn-token-tunel/cx/gpt-5.4
worker-test   → gpt-gmn-token-tunel/cx/gpt-5.5
```

## B-010 verification

Request sent in Discord `#leej` for `sprint11-test-3`:

```text
!run "Viết hàm Python tính tổng các số chẵn trong một danh sách. Có unit test."
```

Batch:

```text
B-010
```

Runtime actions showed all jobs use `sessions_send`:

```text
TASK-032 → agent:software:project-5-worker-hermes → dispatchMethod=sessions_send
TASK-033 → agent:software:project-5-worker-code   → dispatchMethod=sessions_send
TASK-034 → agent:software:project-5-worker-code   → dispatchMethod=sessions_send
```

Runtime actions file:

```text
vaults/openclaw-ai/03-logs/B-010-runtime-actions.json
```

B-010 result:

```text
Pass — sessions_send dispatch worked end-to-end.
```

## Verification commands

```bash
python3 -m py_compile discord/bridge.py leej/dispatcher.py leej/run.py
python3 discord/store.py
```

Expected:

```text
store smoke test OK
```

## Files changed

```text
discord/store.py
discord/channel_manager.py
discord/bridge.py
leej/dispatcher.py
leej/run.py
docs/sprint-11.md
vaults/openclaw-ai/05-retrospective/sprint-11.md
```
