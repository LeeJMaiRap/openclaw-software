# OpenClaw AI

OpenClaw AI is a Docker-first, Discord-driven multi-agent software development system.

A user sends a command in Discord. LeeJ Agent plans the request into structured tasks. OpenClaw worker sessions execute those tasks. The checker verifies filesystem evidence. When a batch passes, task branches and GitHub pull requests can be created automatically. Results, artifacts, and PR links return to Discord.

## Current status

- Main branch: `main`
- Remote: `https://github.com/LeeJMaiRap/openclaw-software.git`
- Latest completed sprint: **Sprint 14**
- Production interface: Discord project workspaces
- PR automation: available after workers finish and `leej/checker.py --batch <batch_id>` passes

## Architecture

```text
Discord
  └─ discord/bridge.py
       ├─ project category/channel routing
       ├─ pipeline trigger
       ├─ result/artifact delivery
       └─ PR URL parsing/posting

LeeJ pipeline
  ├─ leej/leej_agent.py      → request planning and task generation
  ├─ leej/dispatcher.py      → task dispatch plan and runtime handoff
  ├─ leej/run.py             → pipeline preparation/orchestration entrypoint
  ├─ leej/checker.py         → acceptance criteria verification
  ├─ leej/pr_creator.py      → checked task → git branch/commit/PR
  ├─ leej/llm_client.py      → 9Router/OpenAI-compatible LLM calls
  └─ leej/model_health.py    → model health probes

OpenClaw runtime
  ├─ persistent worker sessions
  ├─ sessions_send dispatch contracts
  ├─ dependency waves
  └─ absolute output/done-log paths

Persistence
  ├─ tasks/*.json
  ├─ vaults/openclaw-ai/01-tasks/
  ├─ vaults/openclaw-ai/02-outputs/
  ├─ vaults/openclaw-ai/03-logs/
  ├─ vaults/openclaw-ai/04-decisions/
  ├─ vaults/openclaw-ai/05-retrospective/
  └─ discord/state.sqlite3   → local Discord mapping store, ignored by Git
```

## Core components

- **LeeJ Agent**: coordinator and project manager.
- **LLM planner**: converts user requests into JSON task plans.
- **Dispatcher**: builds worker prompts, dependency waves, and runtime action files.
- **Worker agents**: execute tasks through OpenClaw persistent sessions.
- **Checker**: verifies task output files and done logs against acceptance criteria.
- **PR creator**: creates task branches and GitHub pull requests after checker pass.
- **Discord bridge**: receives commands, creates project channels, runs pipelines, and posts results/PRs.
- **SQLite mapping store**: maps Discord projects, roles, channels, tasks, and workers.
- **Obsidian-style vault**: stores tasks, outputs, logs, decisions, and retrospectives.

## Requirements

- Docker Desktop or compatible Docker runtime
- Python 3.11+
- Git
- GitHub CLI (`gh`) authenticated as a repo-capable account
- Discord bot token
- Discord bot permissions:
  - View Channels
  - Send Messages
  - Attach Files
  - Manage Channels
  - Read Message History
  - Message Content Intent enabled in Discord Developer Portal
- 9Router or OpenAI-compatible API key configured in the OpenClaw environment
- OpenClaw runtime with session tools and model routing configured

## GitHub CLI auth persistence

GitHub CLI auth is restored on bridge startup by `discord/setup_ssh.sh`.

Persistent auth location:

```text
/data/.openclaw/gh/hosts.yml
```

Runtime restore target:

```text
/root/.config/gh/hosts.yml
```

Verify:

```bash
gh auth status
gh repo view LeeJMaiRap/openclaw-software --json name,url
```

## Quick setup

Clone the repository:

```bash
git clone https://github.com/LeeJMaiRap/openclaw-software.git
cd openclaw-software
```

Create Discord environment file:

```bash
cp discord/.env.example discord/.env
```

Edit `discord/.env`:

```text
DISCORD_BOT_TOKEN=your-token
DISCORD_GUILD_ID=your-guild-id
DISCORD_INPUT_CHANNEL_ID=legacy-input-channel-id
DISCORD_OUTPUT_CHANNEL_ID=legacy-output-channel-id
```

Install Discord dependencies:

```bash
python3 -m venv discord/.venv
discord/.venv/bin/pip install -r discord/requirements.txt
```

Verify env loading:

```bash
bash discord/load_env.sh >/dev/null && echo "env OK"
```

Start the bridge:

```bash
bash discord/start_bridge.sh
```

Run healthcheck:

```bash
bash discord/healthcheck.sh
```

## Discord commands

Create a project workspace:

```text
!project create <name>
```

This creates:

```text
Category: <name>
  #leej
  #workers
  #results
  #artifacts
  #worker-code
  #worker-hermes
  #worker-test
```

Run a software task from project `#leej`:

```text
!run "Build a simple Python module with unit tests."
```

List projects:

```text
!project list
```

Archive project:

```text
!project done <name>
```

Queue fix request:

```text
!fix TASK-123 describe the requested change
```

Legacy Sprint 6 mode remains supported: `!run "..."` in the configured input channel posts to the configured output channel.

## Running locally

Prepare a pipeline:

```bash
python3 leej/run.py "Write a Python factorial function using recursion. Include unit tests."
```

Prepare with auto-PR mode enabled. This only creates PRs if checker can pass at that time:

```bash
python3 leej/run.py --auto-pr "Write a Python module with tests."
```

Check a batch:

```bash
python3 leej/checker.py --batch B-012
```

Emit PR-ready markers after a full pass:

```bash
python3 leej/checker.py --batch B-012 --auto-pr
```

Create a task PR after checker pass:

```bash
python3 leej/pr_creator.py \
  --task-id TASK-039 \
  --batch-id B-012 \
  --project sprint14-test
```

Run tests:

```bash
python3 -m unittest discover -s tests
```

Compile core files:

```bash
python3 -m py_compile \
  discord/store.py discord/channel_manager.py discord/bridge.py \
  leej/run.py leej/checker.py leej/pr_creator.py
```

## PR automation flow

```text
1. LeeJ prepares batch and runtime actions.
2. OpenClaw workers execute tasks and write output/done logs.
3. Checker runs on whole batch.
4. If checker passes 100%, pr_creator runs per task.
5. pr_creator creates an isolated git worktree.
6. pr_creator copies related files into the worktree.
7. pr_creator commits, pushes branch, runs gh pr create.
8. Discord bridge posts PR URLs to #results/#artifacts.
```

Important: `leej/run.py` prepares runtime handoff. It does not wait for workers to finish. PR creation must occur after worker completion and a real checker pass.

## Repository layout

```text
.
├── discord/
│   ├── bridge.py
│   ├── channel_manager.py
│   ├── healthcheck.sh
│   ├── load_env.sh
│   ├── requirements.txt
│   ├── setup_ssh.sh
│   ├── start_bridge.sh
│   └── store.py
├── docs/
│   ├── sprint-0.md
│   ├── ...
│   └── sprint-14.md
├── leej/
│   ├── checker.py
│   ├── dispatcher.py
│   ├── fix_requests.py
│   ├── leej_agent.py
│   ├── llm_client.py
│   ├── model_health.py
│   ├── pr_creator.py
│   └── run.py
├── tasks/
├── tests/
└── vaults/openclaw-ai/
    ├── 00-overview/
    ├── 01-tasks/
    ├── 02-outputs/
    ├── 03-logs/
    ├── 04-decisions/
    └── 05-retrospective/
```

## Security notes

Do not commit secrets or runtime state.

Ignored files include:

```text
discord/.env
discord/bridge.log
discord/healthcheck.log
discord/state.sqlite3
```

If a Discord bot token or GitHub PAT is exposed, rotate it immediately.

## Model routing

Current production routing:

```text
claude-cli → gpt-gmn-token-tunel/cx/gpt-5.5
codex-cli  → gpt-gmn-token-tunel/cx/gpt-5.4
hermes     → gpt-gmn-token-tunel/cx/gpt-5.4
manual     → no spawned session
```

Check model health:

```bash
python3 leej/model_health.py --all
```

## Sprint history

- Sprint 0 — Project foundation
- Sprint 1 — LeeJ agent and basic workflow
- Sprint 2 — Batch tasks and dependencies
- Sprint 3 — Pipeline orchestrator
- Sprint 4 — Model health and routing
- Sprint 5 — LLM task planning
- Sprint 6 — Discord MVP
- Sprint 7 — Full Discord project workspaces
- Sprint 8 — Bridge as service
- Sprint 9 — GitHub remote and project documentation
- Sprint 10 — SSH key persistence and GitHub remote ops
- Sprint 11 — Persistent worker sessions and `sessions_send` dispatch
- Sprint 12 — Fix queue workflow
- Sprint 13 — Worker absolute path fix and path audit
- Sprint 14 — GitHub PR automation, gh CLI persistence, worktree-based `pr_creator.py`
