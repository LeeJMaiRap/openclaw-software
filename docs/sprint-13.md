# Sprint 13 — Worker absolute path fix + PR prep

## Status

✅ Done — closed on 2026-06-09 12:01 UTC.

## Goal

Prevent worker sessions from writing outputs to the wrong workspace root.

Wrong path seen in earlier sprints:

```text
/data/workspace/vaults/...        ❌
```

Correct path:

```text
/data/workspace/openclaw-ai/vaults/... ✅
```

Root cause:

```text
Worker bootstrap/task/fix prompts were not explicit enough about absolute paths.
```

## Audit

Command:

```bash
grep -n "workspace\|output.*path\|vaults" \
  discord/bridge.py leej/dispatcher.py \
  leej/fix_requests.py | grep -v ".pyc"
```

Audited 3 path-injection areas:

```text
1. discord/bridge.py
   - worker bootstrap prompt
   - fix request worker message builder

2. leej/dispatcher.py
   - task message sent via sessions_send

3. leej/fix_requests.py
   - queue helper only; no worker-facing prompt template
```

## Patch 1 — worker bootstrap prompt

File:

```text
discord/bridge.py
```

Function:

```text
build_worker_bootstrap_prompt()
```

Added explicit block using `WORKDIR`:

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

## Patch 2 — task message template

File:

```text
leej/dispatcher.py
```

Function:

```text
worker_message()
```

Replaced relative paths with exact absolute paths:

```text
OUTPUT REQUIREMENTS:
- Write output to EXACT path:
  /data/workspace/openclaw-ai/vaults/openclaw-ai/02-outputs/<TASK_ID>-output.md
- Write done log to EXACT path:
  /data/workspace/openclaw-ai/vaults/openclaw-ai/03-logs/<TASK_ID>-done.md
- All source code files under:
  /data/workspace/openclaw-ai/
- NEVER use /data/workspace/ as root
- NEVER use relative paths
```

Removed old weaker block:

```text
IMPORTANT: All output files must be written to absolute path:
/data/workspace/openclaw-ai/
```

## Patch 3 — fix request message

File:

```text
discord/bridge.py
```

Function:

```text
build_fix_worker_message()
```

Changed worker-facing fix request from relative context path to full absolute paths.

Now includes:

```text
IMPORTANT PATHS:
- Current output: /data/workspace/openclaw-ai/vaults/openclaw-ai/02-outputs/<TASK_ID>-output.md
- Write fixed output to SAME path (overwrite)
- Write done log to: /data/workspace/openclaw-ai/vaults/openclaw-ai/03-logs/<TASK_ID>-done.md
- NEVER write to /data/workspace/ directly
- NEVER use relative paths
```

Confirmed no `relative_to()` remains in message builders.

Remaining `relative_to()` hits are metadata/error-display only, not worker instructions.

## Verification

Compile and store smoke:

```bash
python3 -m py_compile discord/bridge.py leej/dispatcher.py
python3 discord/store.py
```

Results:

```text
py_compile pass
store smoke test OK
```

Generated dispatcher task message was checked and showed absolute paths:

```text
/data/workspace/openclaw-ai/vaults/openclaw-ai/02-outputs/TASK-032-output.md
/data/workspace/openclaw-ai/vaults/openclaw-ai/03-logs/TASK-032-done.md
```

Bridge restarted safely via `/proc` scan + `nohup`.

Bridge online confirmation:

```text
Bridge ready. Listening... guild=1513047758636978256 input=1513057505113280622 output=1513057557596602378
```

## End-to-end test

Project:

```text
sprint13-test
```

Batch:

```text
B-011
```

User reported:

```text
B-011 pass
```

Path verification:

```bash
find /data/workspace/openclaw-ai/vaults/openclaw-ai/02-outputs \
 -name "TASK-03*-output.md" | sort | tail -5
```

Output:

```text
/data/workspace/openclaw-ai/vaults/openclaw-ai/02-outputs/TASK-030-output.md
/data/workspace/openclaw-ai/vaults/openclaw-ai/02-outputs/TASK-031-output.md
/data/workspace/openclaw-ai/vaults/openclaw-ai/02-outputs/TASK-032-output.md
```

Wrong-root check:

```bash
find /data/workspace/vaults 2>/dev/null \
 -name "TASK-03*-output.md" | sort | tail -5
```

Output:

```text
(no files)
```

Conclusion:

```text
✅ Worker wrote to correct absolute repo path first time.
✅ No misplaced /data/workspace/vaults TASK-03* outputs.
✅ No follow-up path correction needed.
```

## GitHub PR

Checked:

```bash
gh --version 2>/dev/null || echo "gh not found"
git --version
```

Output:

```text
gh not found
git version 2.39.5
```

Decision:

```text
GitHub PR auto-creation deferred to Sprint 14.
```

Sprint 14 TODO:

```text
Install/configure gh CLI or implement authenticated PR creation path, then add branch + PR automation after checker pass.
```
