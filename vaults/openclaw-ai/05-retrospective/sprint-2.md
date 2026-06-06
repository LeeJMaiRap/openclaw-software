# Sprint 2 Retrospective

## Summary

Sprint 2 delivered batch task creation, dependency graph dispatch, parallel wave orchestration, and batch checking.

Status: ✅ Done
Closed: 2026-06-06 09:46 UTC

## What shipped

- `depends_on` required in task schema.
- `batch_id` optional in task schema.
- Validator semantic checks:
  - self-dependency fails,
  - duplicate dependency fails.
- `leej_agent.py --batch` for heuristic batch splitting.
- `dispatcher.py --batch` for dependency graph waves and batch logging.
- `checker.py --batch` for aggregate task verification.
- Batch B-001 executed end-to-end.

## Batch B-001 result

Tasks:

- TASK-002 — `tinh_trung_binh(data)` — passed.
- TASK-003 — `tinh_trung_vi(data)` — passed.
- TASK-004 — `tinh_do_lech_chuan(data)` — passed.
- TASK-005 — unit tests — passed.

Final checker result:

```text
✅ Batch B-001: 4/4 tasks passed
```

## What worked

- Explicit `depends_on: []` made task dependency state clear.
- Batch heuristic produced exactly the intended task split.
- Dependency graph correctly scheduled:
  - wave 1: TASK-002, TASK-003, TASK-004,
  - wave 2: TASK-005.
- OpenClaw cron tool successfully ran Worker sessions in parallel.
- Batch checker caught missing files before declaring success.

## Issues found

### Worker path issue

Worker sessions wrote output files to:

```text
/data/workspace/vaults/openclaw-ai/...
```

instead of:

```text
/data/workspace/openclaw-ai/vaults/openclaw-ai/...
```

Cause:

- Worker prompt used relative paths.
- Worker session cwd resolved to `/data/workspace`, not repo root.

Recovery:

- Located misplaced files with `find`.
- Copied artifacts into repo vault.
- Re-ran `checker.py --batch B-001` successfully.

Fix applied:

- `dispatcher.py` Worker message now includes absolute output path instruction under `/data/workspace/openclaw-ai/`.

### Model fallback / override

Requested model:

```text
gpt-gmn-token-tunel/cx/gpt-5.3-codex
```

Cron run history reported actual model:

```text
cx/gpt-5.5
```

No run failed, but Sprint 3 should track requested vs actual model in logs.

### Session visibility

`sessions_list` and `sessions_history` visibility is restricted by session tree. Cron run history was more reliable for Worker status.

## Lessons for Sprint 3

- Always use absolute output paths in Worker prompts.
- Batch dispatcher should record requested model and actual runtime model when cron run history is available.
- Checker should remain filesystem-evidence-first, not trust run summaries alone.
- Consider adding a repair command for misplaced artifacts:

```bash
python3 leej/repair_paths.py --from /data/workspace/vaults --to /data/workspace/openclaw-ai/vaults
```

- Consider making dispatcher generate a single structured `dispatch_plan.json` for the runtime bridge.

## Next sprint ideas

- Official runtime bridge for Python dispatcher → OpenClaw cron API/tool.
- Polling/status collector that reads cron run history and updates batch logs.
- Better acceptance checking beyond keyword heuristics.
- Retry policy for failed Worker sessions.
- Centralized model mapping + runtime allowlist/config check.
