# Sprint 14 — GitHub PR Automation

Status: ✅ Done

## Checklist

- ✅ GitHub CLI installed and authenticated.
- ✅ GitHub CLI auth/config persisted from `/root/.config/gh/hosts.yml` into state volume at `/data/.openclaw/gh/hosts.yml`.
- ✅ `discord/setup_ssh.sh` restores gh config on restart:
  - creates `/root/.config/gh`
  - copies persisted `hosts.yml`
  - sets mode `600`
- ✅ `leej/pr_creator.py` added for automated GitHub PR creation.
- ✅ `pr_creator.py` uses temporary `git worktree` per PR to avoid corrupting or mixing the current working tree.
- ✅ Worktree cleanup runs after each PR via `git worktree remove --force`.
- ✅ PR flow implemented:
  1. workers complete task output and done logs
  2. checker passes 100%
  3. `pr_creator.py` creates branch/commit
  4. `gh pr create` opens PR
- ✅ `leej/checker.py --auto-pr` emits PR-ready markers only when a batch fully passes.
- ✅ `leej/run.py --auto-pr` can call checker and PR creator, with PR failures logged without crashing the whole pipeline.
- ✅ `discord/bridge.py` parses PR URLs from pipeline output and posts them back to Discord.
- ✅ PRs are created only after workers have run and checker pass is real.
- ✅ PR URLs are posted to `#results` Discord.

## Verification

GitHub auth verified:

```bash
gh auth status
gh repo view LeeJMaiRap/openclaw-software --json name,url
```

Repo verified:

```json
{"name":"openclaw-software","url":"https://github.com/LeeJMaiRap/openclaw-software"}
```

B-012 checker verified after workers completed:

```text
✅ TASK-038: 3/3 criteria passed
✅ TASK-039: 3/3 criteria passed
✅ TASK-040: 4/4 criteria passed
✅ Batch B-012: 3/3 tasks passed
```

## PRs created

- TASK-038: https://github.com/LeeJMaiRap/openclaw-software/pull/1
- TASK-039: https://github.com/LeeJMaiRap/openclaw-software/pull/2
- TASK-040: https://github.com/LeeJMaiRap/openclaw-software/pull/3

## Important note

`leej/run.py` prepares runtime handoff; it does not wait for OpenClaw workers to finish. Therefore PR creation must happen after worker runtime completion and after a real checker pass. Sprint 14 proved this by manually dispatching B-012 workers, running checker, then creating PRs.
