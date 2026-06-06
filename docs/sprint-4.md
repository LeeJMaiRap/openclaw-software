# Sprint 4 — Model health check, routing fix, fallbackUsed=false

## Status

✅ Done — closed on 2026-06-06 20:51 UTC.

## Goal

Make OpenClaw AI worker routing explicit and healthy:

```text
MODEL_BY_WORKER → health probe → config allowlist → cron runtime summary → checker
```

Sprint 4 focused on model health, routing correctness, and end-to-end proof that Workers no longer silently fall back to another model.

## Checklist

- ✅ Step 1 — Created `leej/model_health.py` with stdlib-only model probe.
- ✅ Step 2 — Added `--all` mode to probe full 9Router catalog.
- ✅ Step 3 — Updated `MODEL_BY_WORKER` to healthy models.
- ✅ Step 4 — Backed up and updated OpenClaw `agents.defaults` model config.
- ✅ Step 5 — Restarted `openclaw-fullpower` from Docker host.
- ✅ Step 6 — Verified default worker model health: `3/3 healthy, 0 unhealthy`.
- ✅ Step 7 — Ran end-to-end pipeline with prime-number task.
- ✅ Step 8 — Confirmed cron `fallbackUsed: false` and checker pass.

## Files changed

```text
leej/model_health.py
leej/dispatcher.py
leej/leej_agent.py
prime.py
tests/test_prime.py
tasks/TASK-010.json
tasks/TASK-011.json
vaults/openclaw-ai/01-tasks/TASK-010.md
vaults/openclaw-ai/01-tasks/TASK-011.md
vaults/openclaw-ai/02-outputs/TASK-010-output.md
vaults/openclaw-ai/02-outputs/TASK-011-output.md
vaults/openclaw-ai/03-logs/B-003-batch.md
vaults/openclaw-ai/03-logs/B-003-check.md
vaults/openclaw-ai/03-logs/B-003-dispatch-plan.json
vaults/openclaw-ai/03-logs/B-003-pipeline.md
vaults/openclaw-ai/03-logs/B-003-runtime-actions.json
vaults/openclaw-ai/03-logs/TASK-010-done.md
vaults/openclaw-ai/03-logs/TASK-011-done.md
vaults/openclaw-ai/03-logs/model-health.json
```

External config backup:

```text
/data/.openclaw/openclaw.json.bak-sprint4-model-health-20260606T204335Z
```

## Step 1 — Model health checker

Added:

```text
leej/model_health.py
```

Default mode checks the worker mapping from `leej/dispatcher.py`:

```bash
python3 leej/model_health.py --timeout 15
```

`--all` mode fetches 9Router catalog and probes every model:

```bash
python3 leej/model_health.py --all --timeout 15
```

Report path:

```text
vaults/openclaw-ai/03-logs/model-health.json
```

The checker uses Python stdlib only:

- `argparse`
- `json`
- `urllib.request`
- `urllib.error`
- `pathlib`
- `datetime`
- `importlib.util`

## Full catalog findings

`--all` catalog probe result:

```text
Summary: 7/33 healthy, 26 unhealthy
```

### cx/gpt-5.3-codex* unusable

All `cx/gpt-5.3-codex*` models failed with HTTP 400 under the current account.

Representative error:

```text
The 'gpt-5.3-codex' model is not supported when using Codex with a ChatGPT account.
```

Affected family:

```text
cx/gpt-5.3-codex
cx/gpt-5.3-codex-high
cx/gpt-5.3-codex-high-review
cx/gpt-5.3-codex-low
cx/gpt-5.3-codex-low-review
cx/gpt-5.3-codex-none
cx/gpt-5.3-codex-none-review
cx/gpt-5.3-codex-review
cx/gpt-5.3-codex-spark
cx/gpt-5.3-codex-spark-review
cx/gpt-5.3-codex-xhigh
cx/gpt-5.3-codex-xhigh-review
```

Decision:

```text
Do not use cx/gpt-5.3-codex* for production Worker tasks on this account.
```

### Gemini probe issue

Gemini models returned HTTP 200 with Server-Sent Events stream (`data: ...`) instead of a single JSON chat completion response.

Observed pattern:

```text
non-JSON response HTTP 200: data: {...}
```

Sprint 4 health checker treats those as unhealthy because the probe parser expects non-stream JSON.

Sprint 5 backlog:

```text
Fix model_health.py to support SSE stream responses and parse first valid completion chunk.
```

Some Gemini models also hit quota errors:

```text
HTTP 429: quota exceeded
```

### fm/* and freemodel-* timeout

The following families timed out or returned malformed/truncated non-JSON within the probe timeout:

```text
fm/gpt-5.3-codex
fm/gpt-5.4
fm/gpt-5.4-mini
fm/gpt-5.5
freemodel-gpt-5-3-codex
freemodel-gpt-5-4
```

Decision:

```text
Do not route production Worker tasks to fm/* or freemodel-* until a longer/different probe proves reliability.
```

## Healthy models

Healthy catalog models found:

```text
gpt-gmn-token-tunel/cx/gpt-5.5
gpt-gmn-token-tunel/cx/gpt-5.4
gpt-gmn-token-tunel/cx/gpt-5.4-mini
gpt-gmn-token-tunel/cx/gpt-5.4-mini-review
gpt-gmn-token-tunel/cx/gpt-5.4-review
gpt-gmn-token-tunel/cx/gpt-5.5-review
gpt-gmn-token-tunel/vohantoken
```

Production pool chosen for allowlist:

```text
gpt-gmn-token-tunel/cx/gpt-5.5
gpt-gmn-token-tunel/cx/gpt-5.4
gpt-gmn-token-tunel/cx/gpt-5.4-mini
gpt-gmn-token-tunel/cx/gpt-5.5-review
gpt-gmn-token-tunel/vohantoken
```

Primary model:

```text
gpt-gmn-token-tunel/cx/gpt-5.5
```

Fallbacks:

```text
gpt-gmn-token-tunel/cx/gpt-5.4
```

## Routing fix

Updated `MODEL_BY_WORKER`:

```python
MODEL_BY_WORKER = {
    "claude-cli": "gpt-gmn-token-tunel/cx/gpt-5.5",
    "codex-cli": "gpt-gmn-token-tunel/cx/gpt-5.4",
    "hermes": "gpt-gmn-token-tunel/cx/gpt-5.4",
}
```

Rationale:

- `gpt-5.5` for ordinary code tasks (`claude-cli`).
- `gpt-5.4` for complex/review-heavy tasks (`codex-cli`, `hermes`).
- Review variants are not used for production Worker tasks.

## Config update

Backed up config before edit:

```text
/data/.openclaw/openclaw.json.bak-sprint4-model-health-20260606T204335Z
```

Updated:

```json
{
  "primary": "gpt-gmn-token-tunel/cx/gpt-5.5",
  "fallbacks": [
    "gpt-gmn-token-tunel/cx/gpt-5.4"
  ]
}
```

Updated allowlist:

```json
{
  "gpt-gmn-token-tunel/cx/gpt-5.5": {},
  "gpt-gmn-token-tunel/cx/gpt-5.4": {},
  "gpt-gmn-token-tunel/cx/gpt-5.4-mini": {},
  "gpt-gmn-token-tunel/cx/gpt-5.5-review": {},
  "gpt-gmn-token-tunel/vohantoken": {}
}
```

Restarted gateway from Docker host:

```bash
docker restart openclaw-fullpower
```

Output:

```text
openclaw-fullpower
```

## Worker health verification

Command:

```bash
python3 leej/model_health.py --timeout 15
```

Result:

```text
Summary: 3/3 healthy, 0 unhealthy
✅ claude-cli | gpt-gmn-token-tunel/cx/gpt-5.5 | healthy
✅ codex-cli | gpt-gmn-token-tunel/cx/gpt-5.4 | healthy
✅ hermes | gpt-gmn-token-tunel/cx/gpt-5.4 | healthy
```

## End-to-end test

Input:

```bash
python3 leej/run.py "Viết hàm Python kiểm tra số nguyên tố.
Có unit test."
```

Generated batch:

```text
B-003
```

Generated tasks:

| Task | Goal | depends_on | Worker | Model |
|---|---|---|---|---|
| TASK-010 | `is_prime(n)` | `[]` | `claude-cli` | `cx/gpt-5.5` |
| TASK-011 | unit test for `is_prime(n)` | `[TASK-010]` | `claude-cli` | `cx/gpt-5.5` |

Runtime jobs:

| Task | Job ID | Cron model | Provider | fallbackUsed | Status |
|---|---|---|---|---|---|
| TASK-010 | `dace62e8-819e-48e4-94ba-d1138f5c6eb8` | `cx/gpt-5.5` | `gpt-gmn-token-tunel` | `false` | `ok` |
| TASK-011 | `606ded1f-e44d-4d6f-8473-83ca584d53e2` | `cx/gpt-5.5` | `gpt-gmn-token-tunel` | `false` | `ok` |

Important confirmation:

```text
fallbackUsed: false
```

This confirms routing used the requested healthy model and no hidden fallback occurred.

## Checker result

Command:

```bash
python3 leej/checker.py --batch B-003
```

Output:

```text
✅ TASK-010: 3/3 criteria passed
✅ TASK-011: 3/3 criteria passed
✅ Batch B-003: 2/2 tasks passed
📝 Check log: vaults/openclaw-ai/03-logs/B-003-check.md
```

Unit test:

```bash
python3 -m unittest tests/test_prime.py
```

Output:

```text
Ran 3 tests in 0.000s
OK
```

## Sprint 5 backlog

- Add SSE parser support for Gemini model probes.
- Separate health classes: `healthy`, `streaming-healthy`, `quota-limited`, `timeout`, `unsupported`.
- Add tests for `model_health.py`.
- Make `run.py` fully autonomous if OpenClaw provides a safe runtime bridge.
- Avoid hand-writing runtime cron payloads by generating them directly from `B-xxx-runtime-actions.json`.
- Add `prime` heuristic tests or generalize task parsing beyond fixed heuristics.
