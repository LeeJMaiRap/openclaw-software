# Sprint 5 Retrospective

## Summary

Sprint 5 replaced fixed batch-task heuristics with LLM-generated task planning.

Status: ✅ Done
Closed: 2026-06-07 05:05 UTC

## What shipped

- `leej/llm_client.py` — stdlib-only client for 9Router chat completions.
- `leej_agent.py --batch` now calls LLM planner for task decomposition.
- JSON-only task-plan prompt with no markdown/backticks.
- Strict parser and validation for LLM plans.
- One retry on LLM call failure, JSON parse failure, or validation failure.
- Clear final failure after retry; no hidden heuristic fallback.
- Three end-to-end runtime tests:
  - B-004 — CSV numeric column sums.
  - B-005 — bubble sort vs quick sort, benchmark, unit tests.
  - B-006 — todo list module with JSON persistence and unit tests.

## Final result

Batches:

```text
B-004: 3/3 tasks passed
B-005: 5/5 tasks passed
B-006: 3/3 tasks passed
```

Runtime routing:

```text
All B-004/B-005/B-006 cron task summaries: fallbackUsed=false
```

Actual runtime-proven count:

```text
B-004 + B-005 + B-006 = 3 + 5 + 3 = 11 tasks
```

Note: Sprint closeout request mentioned `13 tasks`, but dispatch plans and cron summaries show `11` actual tasks across those three batches. The retrospective records the evidence-based count.

Full repo test gate:

```text
python3 -m unittest discover -s tests
Ran 21 tests in 0.015s
OK
```

## What worked

### LLM planner handled new request types

The system generated valid task plans for three different requests without adding a new heuristic per request:

- CSV processing script.
- Sorting algorithms plus benchmark and tests.
- Todo module with JSON persistence and tests.

This is the core Sprint 5 win: new work requests can produce structured multi-agent task batches through an LLM plan.

### Strict JSON contract kept outputs usable

Requiring JSON-only output and validating every field made LLM output safe enough to turn into task files.

Validated fields included:

- `title`
- `goal`
- `acceptance_criteria`
- `worker`
- `depends_on_titles`
- `priority`
- `timeout_minutes`

### Title-based dependencies worked

The LLM planned dependencies using task titles. LeeJ Agent mapped those titles to concrete task IDs after allocation.

This kept prompts natural while preserving strict `depends_on` task IDs in task JSON.

### No hidden fallback improved trust

The old heuristic path was useful in early sprints, but hiding it behind a failed LLM call would make results ambiguous.

Sprint 5 made the behavior explicit:

```text
LLM task planning failed after 2 attempts; no heuristic fallback used.
```

### Runtime model routing remained clean

Worker routing from Sprint 4 stayed correct:

```text
hermes     → cx/gpt-5.4
claude-cli → cx/gpt-5.5
```

Every observed cron summary for Sprint 5 E2E tasks reported:

```text
fallbackUsed: false
```

## Issues found

### Pipeline wording still says prepared while runtime is manual/tool-driven

`leej/run.py` prepares runtime handoff JSON, but actual execution still happens through the OpenClaw cron tool in the assistant runtime.

This remains correct by design, because Python scripts cannot directly call OpenClaw tools without an official bridge/API. But the CLI output can still read confusingly.

Backlog:

```text
Clarify prepared vs executed runtime phases in pipeline output.
```

### Some worker runs took longer than expected to finalize logs

TASK-021 and TASK-022 created code/tests before writing final output and done logs. They eventually completed, but polling looked stalled for a while.

Lesson:

```text
Worker prompts should emphasize writing done logs immediately after verification.
```

### Closeout count mismatch

The requested note said `fallbackUsed=false toàn bộ 13 tasks (B-004, B-005, B-006)`, but evidence shows:

```text
B-004 = 3 tasks
B-005 = 5 tasks
B-006 = 3 tasks
Total = 11 tasks
```

Decision:

```text
Record actual evidence, not requested-but-incorrect count.
```

## Lessons

- LLM task planning is viable when the output schema is strict.
- JSON-only prompts need explicit “no markdown, no backticks” wording.
- One retry is enough for Sprint 5; do not silently fall back.
- Filesystem checker remains the final source of truth for task pass/fail.
- Cron runtime summaries are essential for model/fallback evidence.
- `fallbackUsed=false` must be captured per task, not assumed from config.
- Worker sessions should always write both output and done log before finishing.

## Sprint 6 candidates

- Add automated tests for LLM planner parser and retry behavior.
- Add saved raw LLM response logs for failed parse attempts.
- Add `--dry-run-plan` to preview LLM-generated tasks before writing.
- Improve `run.py` wording around runtime handoff vs execution.
- Build a safe runtime bridge if OpenClaw exposes one.
- Add checker support for code-level tests as first-class criteria.
- Add `model_health.py` SSE parser for Gemini streaming responses.
