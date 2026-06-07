# Sprint 8 — Bridge as service: healthcheck, log rotation, persistent env

## Status

✅ Done — closed on 2026-06-07 11:48 UTC.

## Goal

Harden Discord bridge runtime so it survives crashes and restarts without manually retyping secrets.

Sprint 8 focused on current `openclaw-software` container first. Separate Docker bridge service remains optional follow-up.

## Checklist

- ✅ Added `discord/.env` for persistent local environment variables.
- ✅ `discord/.env` is ignored and not committed.
- ✅ Added `discord/.env.example` for non-secret template.
- ✅ Added `discord/load_env.sh`.
- ✅ `load_env.sh` reads env without printing token.
- ✅ `load_env.sh` exits non-zero when required variables are missing.
- ✅ Added `discord/start_bridge.sh`.
- ✅ `start_bridge.sh` uses `exec discord/.venv/bin/python discord/bridge.py`, so bridge process replaces shell and has stable PID.
- ✅ Updated `discord/bridge.py` to use `logging.handlers.RotatingFileHandler`.
- ✅ Bridge log path: `discord/bridge.log`.
- ✅ Bridge log rotation: max `5MB`, `3` backup files.
- ✅ Added `discord/healthcheck.sh`.
- ✅ `healthcheck.sh` scans `/proc` for bridge PID, no `pgrep` dependency.
- ✅ `healthcheck.sh` logs to separate `discord/healthcheck.log`.
- ✅ `healthcheck.sh` restarts bridge when process is down.
- ✅ OpenClaw cron healthcheck created: every 5 minutes.
- ✅ Reliability test passed: killed bridge PID, healthcheck restarted it.
- ✅ Post-restart Discord `!run` passed: Batch `B-009`, 3/3 tasks.
- ✅ Reminder: rotate Discord Bot Token after sprint.

## Files

```text
discord/.env.example
discord/load_env.sh
discord/start_bridge.sh
discord/healthcheck.sh
discord/bridge.py
.gitignore
```

Ignored runtime files:

```text
discord/.env
discord/bridge.log
discord/state.sqlite3
```

## Environment persistence

Local secret file:

```text
discord/.env
```

Format:

```text
DISCORD_BOT_TOKEN=***
DISCORD_GUILD_ID=1513047758636978256
DISCORD_INPUT_CHANNEL_ID=1513057505113280622
DISCORD_OUTPUT_CHANNEL_ID=1513057557596602378
```

Safety:

- `.env` is ignored.
- Token is not printed by `load_env.sh`.
- Token should still be rotated because it was exposed during earlier manual debugging.

Verification:

```bash
bash discord/load_env.sh >/dev/null && echo "env OK"
```

Output:

```text
env OK
```

## Start script

File:

```text
discord/start_bridge.sh
```

Content:

```bash
#!/bin/bash
set -e
cd /data/workspace/openclaw-ai
source discord/load_env.sh
exec discord/.venv/bin/python discord/bridge.py
```

Why `exec` matters:

```text
The Python bridge replaces the shell process, so PID tracking and signals are simpler.
```

Verification:

```bash
bash -n discord/start_bridge.sh && echo "syntax OK"
ls -la discord/start_bridge.sh
```

Output:

```text
syntax OK
-rwxr-xr-x 1 root root 125 Jun  7 10:31 discord/start_bridge.sh
```

## Log rotation

Bridge logging now uses:

```python
logging.handlers.RotatingFileHandler
```

Settings:

```text
path: discord/bridge.log
maxBytes: 5 * 1024 * 1024
backupCount: 3
```

Startup and Discord client logs go through Python logging. Token is not logged.

## Health check

File:

```text
discord/healthcheck.sh
```

Behavior:

1. Scan `/proc/[0-9]*/cmdline`.
2. Match real Python bridge process:
   ```text
   discord/.venv/bin/python discord/bridge.py
   ```
3. If process exists:
   ```text
   bridge OK PID=<pid>
   ```
4. If missing:
   ```text
   bridge down, restarting
   bridge restarted PID=<pid>
   ```
5. Append logs to:
   ```text
   discord/healthcheck.log
   ```

Verification:

```text
2026-06-07T11:09:56Z bridge OK PID=2779
2026-06-07T11:10:09Z bridge down, restarting
2026-06-07T11:10:09Z bridge restarted PID=3226
```

Process after restart:

```text
bridge alive PID=3226 CMD=discord/.venv/bin/python discord/bridge.py
```

## Cron healthcheck

OpenClaw cron job:

```text
job id: 2146f151-729b-4cef-9972-06293f756f8d
name: discord-bridge-healthcheck
schedule: every 300000ms
sessionTarget: isolated
delivery: none
```

Command run by isolated agent turn:

```bash
bash /data/workspace/openclaw-ai/discord/healthcheck.sh
```

Note:

```text
OpenClaw cron tool does not expose a raw shell-command primitive, so the scheduled job uses an isolated agentTurn to run the healthcheck command.
```

## Post-restart E2E test

Bridge restarted by healthcheck:

```text
PID=3226
```

Discord test in `openclaw-demo/#leej`:

```text
!run "Viết hàm Python tính giai thừa bằng đệ quy. Có unit test."
```

Observed:

```text
#leej: accepted request
#workers: pipeline progress
#results: ✅ Pipeline complete
#artifacts: report/file attachment
```

Batch:

```text
B-009
```

Tasks/model routing:

```text
TASK-029 → gpt-gmn-token-tunel/cx/gpt-5.4
TASK-030 → gpt-gmn-token-tunel/cx/gpt-5.5
TASK-031 → gpt-gmn-token-tunel/cx/gpt-5.5
```

Checker:

```text
✅ TASK-029: 3/3 criteria passed
✅ TASK-030: 4/4 criteria passed
✅ TASK-031: 4/4 criteria passed
✅ Batch B-009: 3/3 tasks passed
```

Unit tests:

```text
python3 -m unittest discover -s tests
.................................
----------------------------------------------------------------------
Ran 33 tests in 0.013s

OK
```

## Verification summary

```bash
bash -n discord/load_env.sh && echo load_env_syntax_OK
bash -n discord/start_bridge.sh && echo start_bridge_syntax_OK
bash -n discord/healthcheck.sh && echo healthcheck_syntax_OK
python3 -m py_compile discord/bridge.py discord/store.py discord/channel_manager.py factorial.py
python3 leej/checker.py --batch B-009
python3 -m unittest discover -s tests
```

All passed.

## Required post-sprint action

Rotate Discord Bot Token:

```text
Discord Developer Portal → Application → Bot → Reset Token
```

Then update local:

```text
discord/.env
```

Restart bridge or let healthcheck recover after manual restart.

## Sprint 9 candidates

- Move bridge into dedicated Docker container with restart policy.
- Add raw command runner or safer cron shell bridge if OpenClaw exposes official primitive.
- Add log rotation for `healthcheck.log` too.
- Add `last_active_at` to project store and auto archive inactive projects after 7 days.
- Add bridge status command in Discord.
