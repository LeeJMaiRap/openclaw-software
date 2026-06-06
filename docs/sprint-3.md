# Sprint 3 — Pipeline orchestrator, runtime handoff, auto poll

## Status

✅ Done — closed on 2026-06-06 13:52 UTC.

## Goal

Build a one-command pipeline entrypoint:

```bash
python3 leej/run.py "<request>"
```

Pipeline shape:

```text
leej_agent.py --batch → dispatcher.py --batch → OpenClaw runtime handoff
→ cron spawn/poll → checker.py --batch → pipeline report
```

## Checklist

- ✅ Step 1 — `dispatcher.py` writes dispatch plan and polling contract.
- ✅ Step 2 — `leej/run.py` generates tasks, dispatch plan, runtime actions, and prepared report.
- ✅ Step 3 — OpenClaw runtime executes runtime handoff, spawns waves, polls cron history, and runs checker.
- ✅ Step 4 — Pipeline report completed; Sprint 3 docs and retrospective written.

## Test case

Input:

```text
Xây dựng module đổi nhiệt độ:
hàm celsius_to_fahrenheit, fahrenheit_to_celsius,
celsius_to_kelvin. Có unit test.
```

Generated batch:

```text
B-002
```

Generated tasks:

| Task | Goal | depends_on | Worker |
|---|---|---|---|
| TASK-006 | `celsius_to_fahrenheit(c)` | `[]` | `claude-cli` |
| TASK-007 | `fahrenheit_to_celsius(f)` | `[]` | `claude-cli` |
| TASK-008 | `celsius_to_kelvin(c)` | `[]` | `claude-cli` |
| TASK-009 | unit test for all 3 functions | `[TASK-006, TASK-007, TASK-008]` | `claude-cli` |

## Step 1 — Dispatcher dispatch plan

`dispatcher.py --batch` now writes:

```text
vaults/openclaw-ai/03-logs/<BATCH_ID>-dispatch-plan.json
```

The plan includes:

- batch id,
- timeout minutes,
- poll interval seconds,
- waves,
- task ids,
- session targets,
- models,
- timeout seconds,
- Worker messages,
- cron payload specs.

It also includes Worker absolute path instructions inherited from Sprint 2:

```text
IMPORTANT: All output files must be written to absolute path:
/data/workspace/openclaw-ai/
```

## Step 2 — `leej/run.py`

Added:

```text
leej/run.py
```

Usage:

```bash
python3 leej/run.py "Xây dựng module đổi nhiệt độ: hàm celsius_to_fahrenheit, fahrenheit_to_celsius, celsius_to_kelvin. Có unit test."
```

`run.py` does not fake OpenClaw tool access. It prepares runtime handoff files:

```text
vaults/openclaw-ai/03-logs/B-002-runtime-actions.json
vaults/openclaw-ai/03-logs/B-002-pipeline.md
```

## Runtime handoff pattern

Sprint 3 established the runtime handoff pattern:

```text
Python prepares, OpenClaw executes.
```

Python scripts handle deterministic repo work:

- task generation,
- dependency graph/wave planning,
- runtime action serialization,
- filesystem reports,
- checker execution.

OpenClaw runtime handles tool work:

- cron job spawn,
- cron run-history polling,
- wave transitions,
- delayed poll wake events.

This avoids inventing a Python API for OpenClaw tools.

## Polling strategy

Used cron run history as source of truth.

Polling did not use long `sleep` loops. Runtime used poll wake events between checks.

Wave completion rule:

- move forward when all jobs have status `ok` or `error`,
- if `ok`: task passed dispatch stage,
- if `error`: log warning and continue pipeline,
- checker remains filesystem-evidence-first.

## Step 3 — Runtime execution

Wave 1:

- TASK-006 → ok, 29.2s
- TASK-007 → ok, 27.3s
- TASK-008 → ok, 36.6s

Wave 2:

- TASK-009 → ok, 62.8s

Batch log:

```text
vaults/openclaw-ai/03-logs/B-002-batch.md
```

Checker:

```bash
python3 leej/checker.py --batch B-002
```

Result:

```text
✅ TASK-006: 3/3 criteria passed
✅ TASK-007: 3/3 criteria passed
✅ TASK-008: 3/3 criteria passed
✅ TASK-009: 3/3 criteria passed
✅ Batch B-002: 4/4 tasks passed
```

## Step 4 — Pipeline report

Final report:

```text
vaults/openclaw-ai/03-logs/B-002-pipeline.md
```

Status:

```text
complete
```

Summary:

```text
✅ Pipeline complete: Batch B-002 — 4/4 tasks passed
```

## Model fallback note

Requested model remained:

```text
gpt-gmn-token-tunel/cx/gpt-5.3-codex
```

Cron history still reported actual model:

```text
cx/gpt-5.5
```

This happened for TASK-006..TASK-009. Needs investigation in Sprint 4.

## Worker path note

Worker output paths were correct in Sprint 3 because Sprint 2 fix worked. Files landed under:

```text
/data/workspace/openclaw-ai/vaults/openclaw-ai/...
```

No misplaced files under `/data/workspace/vaults` were needed.

## Artifacts

Core files:

```text
leej/run.py
leej/dispatcher.py
leej/leej_agent.py
leej/checker.py
```

Batch files:

```text
tasks/TASK-006.json
tasks/TASK-007.json
tasks/TASK-008.json
tasks/TASK-009.json
```

Runtime/log files:

```text
vaults/openclaw-ai/03-logs/B-002-dispatch-plan.json
vaults/openclaw-ai/03-logs/B-002-runtime-actions.json
vaults/openclaw-ai/03-logs/B-002-batch.md
vaults/openclaw-ai/03-logs/B-002-check.md
vaults/openclaw-ai/03-logs/B-002-pipeline.md
```

Generated code:

```text
temperature_conversions.py
tests/test_temperature_conversions.py
```
