# Sprint 9 — GitHub remote, README, issue templates

## Status

✅ Done — closed on 2026-06-07 12:05 UTC.

## Goal

Back up the repository to GitHub, expand public project documentation, and prepare for Sprint 10 worker pull requests.

## Checklist

- ✅ Verified local repository state before push.
- ✅ Confirmed 10 commits before Sprint 9 documentation commit.
- ✅ Confirmed working tree clean before README/template work.
- ✅ Confirmed no sensitive runtime files were tracked:
  - `discord/.env`
  - `discord/bridge.log`
  - `discord/state.sqlite3`
  - `discord/healthcheck.log`
- ✅ Confirmed no remote existed before adding `origin`.
- ✅ Added GitHub remote:
  ```text
  https://github.com/LeeJMaiRap/openclaw-software.git
  ```
- ✅ Renamed branch to `main`.
- ✅ Pushed `main` to GitHub.
- ✅ Verified `origin/main` contains all 10 existing commits.
- ✅ Expanded `README.md` in English.
- ✅ Added GitHub issue templates:
  - `.github/ISSUE_TEMPLATE/bug_report.md`
  - `.github/ISSUE_TEMPLATE/feature_request.md`

## Pre-push verification

Command:

```bash
git log --oneline
```

Output:

```text
89e41a2 feat: Sprint 8 — bridge as service, healthcheck, log rotation, env persistent
356bbdb feat: Sprint 7 — Discord full: category/channel/thread, SQLite mapping
0314944 feat: Sprint 6 — Discord bridge, !run command, pipeline from Discord
cadd521 feat: Sprint 5 — LLM task generation, replace heuristic, llm_client
5f052e4 feat: Sprint 4 — model health check, routing fix, fallbackUsed=false
d60698f feat: Sprint 3 — pipeline orchestrator, runtime handoff, auto poll
3aa3888 feat: Sprint 2 — batch tasks, dependency graph, parallel dispatch
cbde304 feat: Sprint 1 — LeeJ agent, dispatcher, checker, end-to-end flow
9b3a3f8 feat: Sprint 1 — LeeJ agent, dispatcher, checker, end-to-end flow
196d674 chore: Sprint 0 — project scaffold, task schema, Dockerfile, Obsidian vault
```

Command:

```bash
git status
```

Output:

```text
On branch master
nothing to commit, working tree clean
```

Command:

```bash
git remote -v
```

Initial output:

```text
```

No remote existed before Sprint 9.

Command:

```bash
git ls-files | grep -E 'discord/\.env|bridge\.log|state\.sqlite3|healthcheck\.log'
```

Output:

```text
```

No sensitive runtime files were tracked.

## Remote setup

Remote added:

```bash
git remote add origin https://github.com/LeeJMaiRap/openclaw-software.git
```

Verified:

```text
origin  https://github.com/LeeJMaiRap/openclaw-software.git (fetch)
origin  https://github.com/LeeJMaiRap/openclaw-software.git (push)
```

Branch renamed and pushed:

```bash
git branch -M main
git push -u origin main
```

Push output:

```text
To https://github.com/LeeJMaiRap/openclaw-software.git
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.
```

Verified remote history:

```bash
git log --oneline origin/main
```

Output confirmed all 10 commits were present on remote before the Sprint 9 commit.

## README update

`README.md` now documents:

- Project summary
- Architecture
- Core components
- Requirements
- Quick setup
- Discord commands
- Local pipeline commands
- Repository layout
- Security notes
- Model routing
- Sprint history from Sprint 0 through Sprint 9
- Current status and Sprint 10 direction

README language: English.

## Issue templates

Added:

```text
.github/ISSUE_TEMPLATE/bug_report.md
.github/ISSUE_TEMPLATE/feature_request.md
```

Bug report template includes:

- summary
- reproduction steps
- expected behavior
- actual behavior
- evidence
- environment
- impact

Feature request template includes:

- goal
- user story
- proposed behavior
- acceptance criteria
- notes
- priority

## Security notes

GitHub PAT was used for the first push and then removed from the remote URL.

SSH push was configured after the first push.

SSH identity inside the container:

```text
/root/.ssh/openclaw_github
```

Remote URL after SSH setup:

```text
git@github.com:LeeJMaiRap/openclaw-software.git
```

From now on, `git push` from the container does not need a PAT.

Sensitive files remain ignored and untracked:

```text
discord/.env
discord/bridge.log
discord/healthcheck.log
discord/state.sqlite3
```

## Sprint 10 preparation

Sprint 10 target:

```text
Worker creates a branch, commits task output, opens GitHub pull request.
```

Needed next:

- GitHub auth strategy for workers.
- Branch naming convention.
- PR title/body template.
- Reviewer/checker integration.
- Discord result linking to PR URL.
