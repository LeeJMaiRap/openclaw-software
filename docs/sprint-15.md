# Sprint 15 — Runtime Completion Orchestrator

## Status

In progress.

## Goal

Close the gap after Sprint 14: `leej/run.py` prepares runtime handoff, but workers were not executed automatically. Sprint 15 makes Discord project runs continue from prepared batch to worker waves, checker, PR creation, and Discord PR reporting.

Target flow:

```text
!run
→ leej/run.py prepares batch + runtime actions
→ runtime_executor reads B-xxx-runtime-actions.json
→ worker waves execute via OpenClaw persistent sessions
→ checker runs after workers finish
→ pr_creator runs after checker passes
→ PR URLs post to #results/#artifacts
```

## Implementation

### `leej/runtime_executor.py`

New executable orchestrator for prepared batches.

Responsibilities:

- read `vaults/openclaw-ai/03-logs/B-xxx-runtime-actions.json`
- execute dependency waves in order
- dispatch `sessions_send` contracts via:

```bash
openclaw agent --session-key <worker-session-key> --message <worker-task> --timeout <seconds> --json
```

- stop dependent waves if a worker fails
- run checker after all waves finish:

```bash
python3 leej/checker.py --batch <batch_id> --auto-pr
```

- if checker passes and `--auto-pr` is set, create one PR per ready task:

```bash
python3 leej/pr_creator.py --task-id <task_id> --batch-id <batch_id> --project <project>
```

- write runtime logs:

```text
vaults/openclaw-ai/03-logs/B-xxx-runtime-execution.md
vaults/openclaw-ai/03-logs/B-xxx-runtime-execution.json
```

### `discord/bridge.py`

Project `!run` now:

1. calls `leej/run.py` to prepare the batch
2. extracts `B-xxx`
3. calls `leej/runtime_executor.py --batch-id B-xxx --auto-pr --project <project_name>`
4. posts combined pipeline/runtime output
5. parses PR URLs from combined output
6. posts PR URLs to `#results` or `#artifacts`

## Safety

- PR creation only happens after worker execution and checker pass.
- `pr_creator.py` failures are logged and do not crash the whole runtime executor.
- Worker failure stops dependent waves.
- Runtime output is saved to logs for audit.

## Verification plan

```bash
python3 -m py_compile \
  leej/runtime_executor.py \
  leej/run.py \
  leej/checker.py \
  leej/pr_creator.py \
  discord/bridge.py

python3 discord/store.py
```

End-to-end test:

```text
!project create sprint15-test
!run "Viết hàm Python ... Có unit test."
```

Expected:

- workers spawn without manual `sessions_send`
- checker runs after workers
- PRs are created when checker passes
- PR URLs appear in `#results`
