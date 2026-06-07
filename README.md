# OpenClaw AI

OpenClaw AI is a Docker-first, Discord-driven multi-agent software development system.

A user sends a command in Discord. LeeJ Agent turns the request into structured tasks. Worker agents execute those tasks. The checker verifies filesystem evidence. Results and artifacts return to Discord.

## Architecture

```text
Discord
  └─ discord/bridge.py
       ├─ project category/channel routing
       ├─ pipeline trigger
       └─ result/artifact delivery

LeeJ pipeline
  ├─ leej/leej_agent.py      → request planning and task generation
  ├─ leej/dispatcher.py      → task dispatch plan and runtime handoff
  ├─ leej/run.py             → pipeline orchestrator
  ├─ leej/checker.py         → acceptance criteria verification
  ├─ leej/llm_client.py      → 9Router/OpenAI-compatible LLM calls
  └─ leej/model_health.py    → model health probes

Persistence
  ├─ tasks/*.json
  ├─ vaults/openclaw-ai/01-tasks/
  ├─ vaults/openclaw-ai/02-outputs/
  ├─ vaults/openclaw-ai/03-logs/
  ├─ vaults/openclaw-ai/05-retrospective/
  └─ discord/state.sqlite3   → local Discord mapping store, ignored by Git
```

## Core components

- **LeeJ Agent**: coordinator and project manager.
- **LLM planner**: converts user requests into a JSON task plan.
- **Dispatcher**: builds worker prompts, dependency waves, and runtime actions.
- **Worker agents**: execute tasks through OpenClaw runtime sessions.
- **Checker**: verifies task outputs against strict acceptance criteria.
- **Discord bridge**: receives commands, creates project channels, runs pipelines, and posts results.
- **SQLite mapping store**: maps Discord projects, roles, channels, tasks, and threads.
- **Obsidian-style vault**: stores tasks, outputs, logs, decisions, and retrospectives.

## Requirements

- Docker Desktop or compatible Docker runtime
- Python 3.11+
- Git
- Discord bot token
- Discord bot permissions:
  - View Channels
  - Send Messages
  - Attach Files
  - Manage Channels
  - Read Message History
  - Message Content Intent enabled in Discord Developer Portal
- 9Router or OpenAI-compatible API key configured in the OpenClaw environment
- OpenClaw runtime with model routing configured

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

Install Discord dependency in a venv:

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

Run a healthcheck:

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
```

Run a software task from the project `#leej` channel:

```text
!run "Build a simple Python module with unit tests."
```

List active projects:

```text
!project list
```

Archive a project:

```text
!project done <name>
```

Legacy Sprint 6 mode is still supported: `!run "..."` in the configured input channel posts to the configured output channel.

## Running locally

Run the pipeline directly:

```bash
python3 leej/run.py "Write a Python factorial function using recursion. Include unit tests."
```

Check a batch:

```bash
python3 leej/checker.py --batch B-009
```

Run unit tests:

```bash
python3 -m unittest discover -s tests
```

Compile core Discord files:

```bash
python3 -m py_compile discord/store.py discord/channel_manager.py discord/bridge.py
```

## Repository layout

```text
.
├── discord/
│   ├── bridge.py
│   ├── channel_manager.py
│   ├── healthcheck.sh
│   ├── load_env.sh
│   ├── requirements.txt
│   ├── start_bridge.sh
│   └── store.py
├── docker/
│   └── Dockerfile
├── docs/
│   ├── architecture/
│   ├── sprint-0.md
│   ├── sprint-1.md
│   └── ...
├── leej/
│   ├── checker.py
│   ├── dispatcher.py
│   ├── leej_agent.py
│   ├── llm_client.py
│   ├── model_health.py
│   └── run.py
├── schemas/
├── tasks/
├── tests/
├── validators/
└── vaults/openclaw-ai/
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

If a Discord bot token or GitHub PAT is pasted into chat or logs, rotate it immediately.

## Model routing

Current production routing:

```text
claude-cli → gpt-gmn-token-tunel/cx/gpt-5.5
codex-cli  → gpt-gmn-token-tunel/cx/gpt-5.4
hermes     → gpt-gmn-token-tunel/cx/gpt-5.4
manual     → no spawned session
```

Model health is checked with:

```bash
python3 leej/model_health.py --all
```

## Sprint history

### Sprint 0 — Project foundation

Created repository scaffold, task schema, validator, Dockerfile, and Obsidian-style vault.

### Sprint 1 — LeeJ agent and basic workflow

Added task generation, dispatch, checking, and an end-to-end single-task flow.

### Sprint 2 — Batch tasks and dependencies

Added batch tasks, dependency graph, and parallel dispatch waves.

### Sprint 3 — Pipeline orchestrator

Added `leej/run.py`, runtime handoff files, pipeline report, and auto-polling plan.

### Sprint 4 — Model health and routing

Added model health probes, configured worker model routing, and verified `fallbackUsed=false`.

### Sprint 5 — LLM task planning

Replaced keyword heuristics with a JSON-only LLM planner using `llm_client.py`.

### Sprint 6 — Discord MVP

Added Discord bridge with `!run "..."`, fixed input/output channels, and attachment support.

### Sprint 7 — Full Discord project workspaces

Added SQLite mapping, auto category/channel creation, project commands, role-based channel routing, and archive support.

### Sprint 8 — Bridge as service

Added persistent env loading, `start_bridge.sh`, rotating logs, healthcheck auto-restart, and 5-minute cron supervision.

### Sprint 9 — GitHub remote and project documentation

Pushed the repository to GitHub, expanded README documentation, and added issue templates.

## Current status

- Main branch: `main`
- Remote: `https://github.com/LeeJMaiRap/openclaw-software.git`
- Latest completed sprint: Sprint 9
- Next planned sprint: Sprint 10 — worker-created pull requests
