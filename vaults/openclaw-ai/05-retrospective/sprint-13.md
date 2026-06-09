# Sprint 13 Retrospective — Worker absolute path fix

## Result

✅ Done.

Sprint 13 fixed repeated worker output path mistakes by making absolute path requirements explicit in every worker-facing prompt.

## What happened

Workers previously wrote outputs under the wrong root:

```text
/data/workspace/vaults/...        ❌
/data/workspace/openclaw-ai/...   ✅
```

This happened at least twice:

```text
Sprint 2 — misplaced outputs
Sprint 12 — !fix worker wrote wrong root until LeeJ corrected it
```

## Root cause

Worker bootstrap prompt and task/fix messages allowed ambiguity:

```text
relative paths existed
absolute root was not repeated strongly enough
workers could infer /data/workspace as root
```

## Fixes

### 1. Bootstrap prompt

`discord/bridge.py` now injects:

```text
IMPORTANT — ABSOLUTE PATHS:
Workspace root: /data/workspace/openclaw-ai/
Output files:   /data/workspace/openclaw-ai/vaults/openclaw-ai/02-outputs/
Done logs:      /data/workspace/openclaw-ai/vaults/openclaw-ai/03-logs/
Source code:    /data/workspace/openclaw-ai/
NEVER write to: /data/workspace/ (wrong root)
NEVER use relative paths.
ALWAYS use full absolute paths starting with /data/workspace/openclaw-ai/
```

### 2. Task message

`leej/dispatcher.py` now gives exact per-task absolute paths:

```text
/data/workspace/openclaw-ai/vaults/openclaw-ai/02-outputs/<TASK_ID>-output.md
/data/workspace/openclaw-ai/vaults/openclaw-ai/03-logs/<TASK_ID>-done.md
```

### 3. Fix request message

`discord/bridge.py` fix messages now instruct overwrite of exact output path and done log path, with explicit wrong-root warning.

## Verification

Compile + smoke:

```text
python3 -m py_compile discord/bridge.py leej/dispatcher.py
python3 discord/store.py → store smoke test OK
```

End-to-end:

```text
sprint13-test
B-011 pass
```

Path check:

```text
Correct repo outputs present under:
/data/workspace/openclaw-ai/vaults/openclaw-ai/02-outputs/

Wrong root had no TASK-03* outputs:
/data/workspace/vaults/
```

## PR automation

`gh` absent:

```text
gh not found
```

Moved to Sprint 14 TODO:

```text
Add GitHub PR automation after checker pass once gh CLI/API path is available.
```

## Lesson

Worker prompts must name exact absolute paths, not just a root or relative path. Repeating the wrong-root negative constraint is useful:

```text
NEVER write to /data/workspace/
ALWAYS write under /data/workspace/openclaw-ai/
```
