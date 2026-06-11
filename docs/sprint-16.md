# Sprint 16 — Runtime Hardening and Operator UX

## Status

In progress.

## Goal

Harden Sprint 15 runtime execution so project runs are easier to operate and failures are clearer.

## Shipped

### Runtime executor hardening

`leej/runtime_executor.py` now supports:

- worker retry configuration:

```bash
--retries 1
--retry-delay-seconds 10
```

- clearer cron-mode failure message when a batch was prepared without project worker session keys
- checker failure summary extraction
- `CHECKER_FAIL:` lines in stdout for Discord/operator visibility
- PR creation still gated behind checker pass

### Batch cleanup helper

New utility:

```bash
python3 leej/cleanup_batch.py --batch-id B-014
python3 leej/cleanup_batch.py --batch-id B-014 --mode delete
```

Default mode lists generated artifacts only. Delete mode removes batch task files, vault task markdown, outputs, done logs, dispatch logs, and batch logs.

### Project done summary

`!project done <name>` summary now includes, when available:

- batch id
- runtime status from `B-xxx-runtime-execution.json`
- PR URLs
- checker failures
- checker output

## Safety

- Delete cleanup is explicit via `--mode delete`.
- Runtime still stops dependent waves after worker failure.
- PRs are never created unless checker returns success.

## Verification

```bash
python3 -m py_compile \
  leej/runtime_executor.py \
  leej/cleanup_batch.py \
  discord/bridge.py

python3 discord/store.py
python3 leej/cleanup_batch.py --batch-id B-014 --mode list
python3 leej/runtime_executor.py --batch-id B-013 --project sprint15-test --auto-pr --retries 0
```

Expected for B-013 cron-mode check:

```text
unsupported dispatchMethod=cron. This batch was prepared without project worker session keys.
```
