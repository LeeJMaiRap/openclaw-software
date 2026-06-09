# Sprint 12 — Fix queue + project done lifecycle

## Status

In progress — 2026-06-09.

## Goal

Add human-in-loop fixes without pretending the Discord bridge can call OpenClaw `sessions_send` directly.

Sprint 12 uses a file-backed fix queue:

```text
Discord bridge writes fix request JSON
LeeJ runtime session reads pending requests
LeeJ uses tool sessions_send to persistent worker session
Worker fixes output/done log
LeeJ runs checker
LeeJ posts result to Discord #results
LeeJ marks request done/failed
```

## Correct fix workflow

Important: LeeJ runtime must already be online before the Discord `!fix` request is sent.

Correct order:

```text
1. User opens OpenClaw chat and sends: xử lý fix requests
   → LeeJ is online
   → runtime tool sessions_send is available
   → LeeJ starts watching/processing the pending fix queue

2. User sends in Discord project #leej:
   !fix TASK-xxx "mô tả"
   → Discord bot writes fix-request JSON
   → Discord bot posts pending status
   → LeeJ, already online in OpenClaw chat, processes it immediately
```

Wrong order:

```text
1. User sends Discord !fix first
2. Then user opens OpenClaw chat and asks LeeJ to process
```

That delayed order works only as a manual fallback, not the intended live Sprint 12 workflow.

## Why this workflow exists

Current confirmed limitation:

```text
Python Discord bridge cannot call OpenClaw runtime tool sessions_send.
```

Checked and unavailable:

```text
openclaw sessions send CLI
/api/sessions/send
/api/chat
/openapi.json
/api index
active /api/v1/admin/rpc
```

Therefore `!fix` must not fake worker dispatch. It only records a queue item. LeeJ runtime performs the real `sessions_send` call.

## `!fix` command

Syntax in project `#leej`:

```text
!fix TASK-xxx "mô tả"
```

Bridge behavior:

```text
parse task_id + fix_description
resolve Discord project from current #leej channel
load tasks/TASK-xxx.json
map task worker to project worker role
lookup worker session_key from SQLite workers table
write vaults/openclaw-ai/03-logs/fix-requests/TASK-xxx-fix.json
post #leej confirmation
post #workers pending status
```

Worker role mapping:

```text
claude-cli → worker-code
codex-cli  → worker-code
hermes     → worker-hermes
```

Queue file shape:

```json
{
  "task_id": "TASK-xxx",
  "fix_description": "...",
  "requested_at": "<UTC>",
  "status": "pending",
  "project_id": 5,
  "worker_role": "worker-hermes",
  "worker_session_key": "agent:software:project-5-worker-hermes",
  "message": "[FIX REQUEST] ..."
}
```

Discord messages:

```text
#leej:
📝 Fix request TASK-xxx đã ghi.
Nhắn LeeJ 'xử lý fix requests' để tiến hành.

#workers:
⏳ TASK-xxx: fix request pending
```

Note: confirmation text mentions the fallback instruction, but intended live mode is still: start LeeJ first, then send `!fix`.

## LeeJ runtime processing

When user sends in OpenClaw chat:

```text
xử lý fix requests
```

LeeJ should:

```text
1. Run: python3 leej/fix_requests.py pending
2. For each pending request:
   - call sessions_send(worker_session_key, message)
   - wait for worker reply
   - verify expected output/done log paths under /data/workspace/openclaw-ai
   - run checker for the task
   - post result to Discord #results
   - mark request done or failed
```

Helper commands:

```bash
python3 leej/fix_requests.py pending
python3 leej/fix_requests.py message TASK-032
python3 leej/fix_requests.py mark TASK-032 done --note "..." --worker-reply "..."
python3 leej/fix_requests.py mark TASK-032 failed --note "..."
```

## Verified example

Request:

```text
TASK-032 — Thêm xử lý edge case: danh sách rỗng
```

Worker session:

```text
agent:software:project-5-worker-hermes
```

First worker reply wrote wrong workspace root:

```text
/data/workspace/vaults/openclaw-ai/02-outputs/TASK-032-output.md
```

LeeJ sent follow-up requiring correct repo path:

```text
/data/workspace/openclaw-ai/vaults/openclaw-ai/02-outputs/TASK-032-output.md
/data/workspace/openclaw-ai/vaults/openclaw-ai/03-logs/TASK-032-done.md
```

Final checker:

```text
✅ TASK-032: 3/3 criteria passed
```

Fix request status:

```text
done
```

## `!project done`

Syntax:

```text
!project done <project-name>
```

Bridge behavior:

```text
lookup project
infer/use batch_id
run python3 leej/checker.py --batch <batch_id>
post summary to #results
archive category as [done] <project-name>
lock core project channels
lock worker channels
mark workers archived in SQLite
reply close confirmation
```

Close message:

```text
✅ Project "<tên>" đã đóng.
Category archived. Sessions closed.
```

## Verification commands

```bash
python3 -m py_compile discord/bridge.py discord/store.py discord/channel_manager.py leej/fix_requests.py
python3 discord/store.py
python3 leej/fix_requests.py pending
```

Expected smoke output:

```text
store smoke test OK
```
