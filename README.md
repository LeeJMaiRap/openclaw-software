# OpenClaw AI

OpenClaw AI is a Docker-first multi-agent software development system.

The system is designed to take a user request, turn it into structured software work, assign tasks to worker agents, verify outputs, and persist project knowledge.

## Sprint 0 Scope

Sprint 0 focuses on the smallest runnable foundation:

1. Create the project directory structure.
2. Define a JSON Schema and validator for worker task files.
3. Create a Dockerfile for the LeeJ Agent runtime.
4. Set up an Obsidian vault structure for long-term project memory.

## Core Components

- **LeeJ Agent**: PM Core agent. Plans, coordinates, reviews, and records work.
- **Worker Layer**: Execution agents such as Claude CLI, Codex CLI, Hermes, or OpenClaw sub-agents.
- **Channels**: Telegram, Discord, or CLI interfaces for user communication.
- **GitHub**: Code and working data storage.
- **NotebookLM**: Read-only reference knowledge base.
- **Obsidian**: Read/write long-term memory vault.

## Repository Layout

```text
openclaw-ai/
  README.md
  docs/
    architecture/
      openclaw_knowledge_base_v2.txt
    sprint-0.md
  schemas/
  validators/
  tasks/
    examples/
  docker/
  vaults/
    openclaw-ai/
      00-overview/
      01-tasks/
      02-outputs/
      03-logs/
      04-decisions/
      05-retrospective/
```

## Verification

Run from `/data/workspace`:

```bash
find openclaw-ai -maxdepth 3 -type d | sort
find openclaw-ai -maxdepth 3 -type f | sort
git status --short
```

## Current Status

Sprint 0 step 1 is complete when the directory layout exists and the architecture document is available at:

```text
openclaw-ai/docs/architecture/openclaw_knowledge_base_v2.txt
```

## Docker Smoke Test

Sprint 0 uses the task validator as the container smoke test. Each `docker run` validates that the runtime is alive and the example task still matches the schema.

Build the image from the repository root:

```bash
docker build -f docker/Dockerfile -t openclaw-ai:leej-sprint0 .
```

Run the smoke test:

```bash
docker run --rm openclaw-ai:leej-sprint0
```

Expected output:

```text
✅ Task file hợp lệ
```

After Sprint 0, this smoke-test command should be replaced by the real LeeJ Agent entrypoint.
