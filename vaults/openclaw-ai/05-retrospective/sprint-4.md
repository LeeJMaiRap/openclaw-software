# Sprint 4 Retrospective

## Summary

Sprint 4 closed the model-routing gap found in Sprint 3.

Status: ✅ Done
Closed: 2026-06-06 20:51 UTC

## What shipped

- `leej/model_health.py` — stdlib-only model health checker.
- `--all` catalog mode using 9Router `/v1/models`.
- Updated `MODEL_BY_WORKER` to healthy production models:
  - `claude-cli` → `gpt-gmn-token-tunel/cx/gpt-5.5`
  - `codex-cli` → `gpt-gmn-token-tunel/cx/gpt-5.4`
  - `hermes` → `gpt-gmn-token-tunel/cx/gpt-5.4`
- Backed up and fixed OpenClaw model config.
- Restarted `openclaw-fullpower` from Docker host.
- Added `is_prime` task heuristic for Sprint 4 E2E test.
- Ran full E2E pipeline B-003.
- Confirmed cron routing with `fallbackUsed: false`.
- Checker passed: `2/2 tasks`.

## Final result

Default worker health:

```text
Summary: 3/3 healthy, 0 unhealthy
```

E2E batch:

```text
B-003
```

Tasks:

- TASK-010 — `is_prime(n)` — passed.
- TASK-011 — unit tests for `is_prime(n)` — passed.

Checker result:

```text
✅ Batch B-003: 2/2 tasks passed
```

Cron runtime confirmation:

```text
TASK-010 model: cx/gpt-5.5, fallbackUsed: false
TASK-011 model: cx/gpt-5.5, fallbackUsed: false
```

## What worked

### Health checker made model failures explicit

Before Sprint 4, model behavior was inferred from cron summaries. Sprint 4 made it testable:

```bash
python3 leej/model_health.py --timeout 15
python3 leej/model_health.py --all --timeout 15
```

The checker now records:

- allowlist membership,
- provider catalog membership,
- live probe status,
- elapsed time,
- exact HTTP/timeout error.

### Routing fix removed hidden fallback

Sprint 3 observed requested model vs actual model mismatch. Sprint 4 fixed the root cause by routing Workers only to healthy models and trimming the allowlist.

The decisive signal was cron history:

```text
fallbackUsed: false
```

### Gateway restart from Docker host worked

The config change required a real container restart. Running from gateway/Docker host succeeded:

```bash
docker restart openclaw-fullpower
```

### Filesystem checker remained reliable

Cron summaries proved runtime status, but checker still used filesystem evidence. This kept the final pass/fail grounded in artifacts.

## Issues found

### cx/gpt-5.3-codex* not usable with current account

All `cx/gpt-5.3-codex*` variants returned unsupported-model errors for this account.

Lesson:

```text
Catalog presence is not enough. Live probe is required.
```

### Gemini streams need parser support

Several Gemini models returned SSE-style stream chunks:

```text
data: {...}
```

The current probe expects single JSON, so those are marked unhealthy. This may be a probe limitation, not necessarily a model failure.

Sprint 5 should add SSE parsing.

### fm/* and freemodel-* unreliable under current timeout

`fm/*` and `freemodel-*` timed out or returned malformed/truncated non-JSON. They should stay out of production routing until proven stable.

### Task generation remains heuristic

Prime-number task required a new fixed heuristic. This was acceptable for Sprint 4, but broader natural-language task planning still needs improvement.

## Lessons

- Health check every model before routing production work to it.
- Keep allowlist narrow: healthy production models only.
- Record both requested model and cron summary model.
- `fallbackUsed: false` is critical evidence for routing correctness.
- Do not assume `/v1/models` means runnable; probe `/chat/completions` too.
- Streaming responses need different health handling than regular JSON responses.
- Config backup before edit is non-negotiable.

## Sprint 5 candidates

- Add SSE parser support to `model_health.py`.
- Add model health categories instead of binary healthy/unhealthy.
- Add automated config update command guarded by backup + preview.
- Add tests for `model_health.py`.
- Generalize `leej_agent.py` task parsing beyond hardcoded heuristics.
- Convert runtime handoff JSON into automatically executed cron jobs through a safe OpenClaw bridge if available.
- Improve dispatcher output wording so prepared/polling/runtime phases are not mixed.
