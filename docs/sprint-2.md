# Sprint 2 — Batch tasks, dependency graph, parallel dispatch

## Status

✅ Done — closed on 2026-06-06 09:46 UTC.

## Checklist

- ✅ Step 1 — Task schema supports `depends_on` and optional `batch_id`.
- ✅ Step 2 — `leej_agent.py --batch` creates B-001 with TASK-002..TASK-005.
- ✅ Step 3 — `dispatcher.py --batch` builds dependency graph and prepares wave dispatch.
- ✅ Step 4 — `checker.py --batch` verifies all tasks in B-001.

## Batch B-001

Input:

```text
Xây dựng một module Python tính toán thống kê cơ bản:
trung bình, trung vị, độ lệch chuẩn. Có unit test.
```

Generated tasks:

| Task | Goal | depends_on | Worker |
|---|---|---|---|
| TASK-002 | `tinh_trung_binh(data)` | `[]` | `claude-cli` |
| TASK-003 | `tinh_trung_vi(data)` | `[]` | `claude-cli` |
| TASK-004 | `tinh_do_lech_chuan(data)` | `[]` | `claude-cli` |
| TASK-005 | unit tests | `[TASK-002, TASK-003, TASK-004]` | `claude-cli` |

## Step 1 — Schema

Updated `schemas/task.schema.json`:

- `depends_on` is required.
- `depends_on` defaults semantically to `[]`, but every task file must write it explicitly.
- `batch_id` is optional.
- `additionalProperties: false` remains enabled.

Updated `validators/validate_task.py` semantic checks:

- self-dependency is rejected.
- duplicate dependency IDs are rejected.

## Step 2 — Batch creation

Added:

```bash
python3 leej/leej_agent.py --batch "..."
```

Output for Sprint 2 test case:

```text
✅ Batch B-001: 4 tasks created
   TASK-002 (no deps) → claude-cli
   TASK-003 (no deps) → claude-cli
   TASK-004 (no deps) → claude-cli
   TASK-005 (deps: TASK-002, TASK-003, TASK-004) → claude-cli
```

All four task files validated successfully.

## Step 3 — Batch dispatch

Added:

```bash
python3 leej/dispatcher.py --batch B-001
```

Dispatcher now:

- reads all tasks in a batch,
- validates dependency graph,
- computes waves,
- writes batch log with lockfile,
- prepares OpenClaw cron `agentTurn` payloads.

Actual runtime spawning is still performed by OpenClaw tools, not by Python.

Wave execution:

- Wave 1: TASK-002, TASK-003, TASK-004 in parallel.
- Wave 2: TASK-005 after wave 1 completed.

Batch log:

```text
vaults/openclaw-ai/03-logs/B-001-batch.md
```

## Step 4 — Batch check

Added:

```bash
python3 leej/checker.py --batch B-001
```

Final result:

```text
✅ TASK-002: 3/3 criteria passed
✅ TASK-003: 3/3 criteria passed
✅ TASK-004: 3/3 criteria passed
✅ TASK-005: 3/3 criteria passed
✅ Batch B-001: 4/4 tasks passed
```

Check log:

```text
vaults/openclaw-ai/03-logs/B-001-check.md
```

## Worker path issue

During Sprint 2, Worker sessions wrote files under:

```text
/data/workspace/vaults/openclaw-ai/...
```

instead of repo path:

```text
/data/workspace/openclaw-ai/vaults/openclaw-ai/...
```

Root cause: Worker prompts used relative paths, and Worker session cwd resolved to `/data/workspace`.

Fix applied to `dispatcher.py`: every Worker message now includes an absolute path instruction:

```text
IMPORTANT: All output files must be written to absolute path:
/data/workspace/openclaw-ai/
Example:
- output → /data/workspace/openclaw-ai/vaults/openclaw-ai/02-outputs/<TASK_ID>-output.md
- done log → /data/workspace/openclaw-ai/vaults/openclaw-ai/03-logs/<TASK_ID>-done.md
```

## Model fallback note

Requested worker model remained:

```text
gpt-gmn-token-tunel/cx/gpt-5.3-codex
```

Cron run history reported actual model:

```text
cx/gpt-5.5
```

No runtime error occurred. This is recorded for Sprint 3 because runtime may override or fallback models.

## Artifacts

Task files:

```text
tasks/TASK-002.json
tasks/TASK-003.json
tasks/TASK-004.json
tasks/TASK-005.json
```

Worker outputs:

```text
vaults/openclaw-ai/02-outputs/TASK-002-output.md
vaults/openclaw-ai/02-outputs/TASK-003-output.md
vaults/openclaw-ai/02-outputs/TASK-004-output.md
vaults/openclaw-ai/02-outputs/TASK-005-output.md
```

Logs:

```text
vaults/openclaw-ai/03-logs/B-001-batch.md
vaults/openclaw-ai/03-logs/B-001-check.md
vaults/openclaw-ai/03-logs/TASK-002-done.md
vaults/openclaw-ai/03-logs/TASK-003-done.md
vaults/openclaw-ai/03-logs/TASK-004-done.md
vaults/openclaw-ai/03-logs/TASK-005-done.md
```
