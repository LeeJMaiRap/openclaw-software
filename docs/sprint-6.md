# Sprint 6 — Discord bridge, !run command, pipeline from Discord

## Status

✅ Done — closed on 2026-06-07 06:07 UTC.

## Goal

Validate Discord as an OpenClaw command channel.

MVP scope:

```text
Discord #openclaw-general
  → !run "<request>"
  → discord/bridge.py
  → python3 leej/run.py "<request>"
  → post summary/report to #openclaw-results
```

Sprint 6 intentionally did not implement auto category/channel/thread creation. That is Sprint 7 scope.

## Checklist

- ✅ Created `discord/bridge.py`.
- ✅ Created `discord/requirements.txt`.
- ✅ Bridge runs inside `openclaw-software` container.
- ✅ Installed `discord.py` through a project venv.
- ✅ Confirmed `discord.py` version: `2.7.1`.
- ✅ Bridge listens for `!run "<request>"` in `#openclaw-general`.
- ✅ Bridge calls `python3 leej/run.py` from `/data/workspace/openclaw-ai`.
- ✅ Bridge posts result to `#openclaw-results`.
- ✅ Output longer than Discord message budget is attached as `.md`.
- ✅ Pipeline request from Discord created batch `B-007`.
- ✅ B-007 checker passed: `3/3 tasks passed`.
- ✅ Full repo tests passed: `Ran 25 tests`, `OK`.

## Runtime setup

Container:

```text
openclaw-software
```

Dependency install:

```bash
python3 -m venv /data/workspace/openclaw-ai/discord/.venv
/data/workspace/openclaw-ai/discord/.venv/bin/pip install discord.py
```

Version check:

```bash
/data/workspace/openclaw-ai/discord/.venv/bin/python -c "import discord; print(discord.__version__)"
```

Observed:

```text
2.7.1
```

Bridge command shape:

```bash
DISCORD_BOT_TOKEN="***" \
DISCORD_GUILD_ID="1513047758636978256" \
DISCORD_INPUT_CHANNEL_ID="1513057505113280622" \
DISCORD_OUTPUT_CHANNEL_ID="1513057557596602378" \
/data/workspace/openclaw-ai/discord/.venv/bin/python \
  /data/workspace/openclaw-ai/discord/bridge.py \
  >> /data/workspace/openclaw-ai/discord/bridge.log 2>&1
```

Token is not stored in repo and should not be logged.

## Bridge behavior

Command format:

```text
!run "Viết hàm Python đảo ngược chuỗi. Có unit test."
```

On accepted command, bot replies in input channel:

```text
⚙️ Đang xử lý yêu cầu của bạn...
```

Then it runs:

```bash
python3 leej/run.py "<request>"
```

Working directory:

```text
/data/workspace/openclaw-ai
```

Output behavior:

- Short output: send normal Discord message.
- Long output: create temporary `.md` file and upload as attachment.
- If pipeline report exists, attach `B-xxx-pipeline.md`.
- Pipeline failure/timeout: post clear error message to output channel.

## Discord E2E test

User message in `#openclaw-general`:

```text
!run "Viết hàm Python đảo ngược chuỗi. Có unit test."
```

Pipeline batch:

```text
B-007
```

Generated tasks:

```text
TASK-023 → hermes     → cx/gpt-5.4
TASK-024 → claude-cli → cx/gpt-5.5
TASK-025 → claude-cli → cx/gpt-5.5
```

Dependency graph:

```text
TASK-023 → TASK-024 → TASK-025
```

Artifacts:

```text
reverse_string.py
tests/test_reverse_string.py
vaults/openclaw-ai/02-outputs/TASK-023-output.md
vaults/openclaw-ai/02-outputs/TASK-024-output.md
vaults/openclaw-ai/02-outputs/TASK-025-output.md
vaults/openclaw-ai/03-logs/TASK-023-done.md
vaults/openclaw-ai/03-logs/TASK-024-done.md
vaults/openclaw-ai/03-logs/TASK-025-done.md
vaults/openclaw-ai/03-logs/B-007-pipeline.md
```

Checker:

```text
✅ TASK-023: 2/2 criteria passed
✅ TASK-024: 3/3 criteria passed
✅ TASK-025: 3/3 criteria passed
✅ Batch B-007: 3/3 tasks passed
```

Unit test:

```text
test_empty_string (tests.test_reverse_string.ReverseStringTests.test_empty_string) ... ok
test_regular_string (tests.test_reverse_string.ReverseStringTests.test_regular_string) ... ok
test_single_character (tests.test_reverse_string.ReverseStringTests.test_single_character) ... ok
test_spaces_and_special_characters (tests.test_reverse_string.ReverseStringTests.test_spaces_and_special_characters) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
```

Full repo test:

```text
python3 -m unittest discover -s tests
..........................
----------------------------------------------------------------------
Ran 25 tests in 0.008s

OK
```

## Important implementation note

`leej/run.py` still prepares pipeline/runtime handoff. Direct OpenClaw cron execution from Python is not implemented. For B-007, runtime task completion was verified with filesystem artifacts and checker output.

This limitation remains known from earlier sprints:

```text
Python scripts cannot directly call OpenClaw cron tool unless an official bridge/API exists.
```

Sprint 6 validates the Discord command bridge and result posting path. Sprint 7 should integrate runtime execution more cleanly before adding category/thread automation.

## Files added or changed

```text
discord/bridge.py
discord/requirements.txt
reverse_string.py
tests/test_reverse_string.py
tasks/TASK-023.json
tasks/TASK-024.json
tasks/TASK-025.json
vaults/openclaw-ai/01-tasks/TASK-023.md
vaults/openclaw-ai/01-tasks/TASK-024.md
vaults/openclaw-ai/01-tasks/TASK-025.md
vaults/openclaw-ai/02-outputs/TASK-023-output.md
vaults/openclaw-ai/02-outputs/TASK-024-output.md
vaults/openclaw-ai/02-outputs/TASK-025-output.md
vaults/openclaw-ai/03-logs/B-007-*.md/json
vaults/openclaw-ai/03-logs/TASK-023-done.md
vaults/openclaw-ai/03-logs/TASK-024-done.md
vaults/openclaw-ai/03-logs/TASK-025-done.md
```

## Sprint 7 candidates

- Run bridge under supervised process manager.
- Add Dockerfile/container separation for `discord-bridge`.
- Add auto category/thread creation.
- Add Discord channel/thread mapping state.
- Add real runtime handoff execution bridge.
- Add structured result summary parser for checker output.
- Add command authorization allowlist.
