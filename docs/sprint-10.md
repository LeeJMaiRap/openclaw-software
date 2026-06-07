# Sprint 10 — SSH key persistence across container restart

## Status

✅ Done — closed on 2026-06-07 12:39 UTC.

## Goal

Make GitHub SSH push work after container restart without manually recreating `/root/.ssh/openclaw_github`.

## Problem

Before Sprint 10, the SSH key existed only inside container runtime:

```text
/root/.ssh/openclaw_github
```

A container restart would remove that runtime file, causing GitHub SSH push to fail until manual setup was repeated.

## Checklist

- ✅ Inspected Docker mounts for `openclaw-software`.
- ✅ Confirmed `/data/.openclaw` is a persistent state volume.
- ✅ Moved SSH key into persistent state volume:
  ```text
  /data/.openclaw/ssh/openclaw_github
  /data/.openclaw/ssh/openclaw_github.pub
  ```
- ✅ Set secure permissions:
  ```text
  /data/.openclaw/ssh → 700
  /data/.openclaw/ssh/openclaw_github → 600
  ```
- ✅ Added `discord/setup_ssh.sh`.
- ✅ `setup_ssh.sh` restores key from state volume into `/root/.ssh`.
- ✅ `setup_ssh.sh` writes SSH config for GitHub.
- ✅ `setup_ssh.sh` runs `ssh-keyscan github.com`.
- ✅ Updated `discord/start_bridge.sh` to run `setup_ssh.sh` before bridge startup.
- ✅ Simulated restart by deleting runtime key/config.
- ✅ Verified key restore works.
- ✅ Verified GitHub SSH auth works after restore.
- ✅ Verified `git push origin main` works after restore.
- ✅ No PAT needed from now on for container Git push.

## Volume inspection

Command:

```bash
docker inspect openclaw-software \
  --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\\n"}}{{end}}'
```

Output:

```text
/var/lib/docker/volumes/openclaw-software-state/_data -> /data/.openclaw
/var/lib/docker/volumes/openclaw-software-workspace/_data -> /data/workspace
/run/desktop/mnt/host/wsl/docker-desktop-bind-mounts/Ubuntu/docker.sock -> /var/run/docker.sock
```

Decision:

```text
Use /data/.openclaw/ssh/ for persistent SSH key storage.
```

## Persistent SSH key location

```text
/data/.openclaw/ssh/openclaw_github
/data/.openclaw/ssh/openclaw_github.pub
```

Verification:

```text
total 16
drwx------  2 root root 4096 Jun  7 12:35 .
drwx------ 13 root root 4096 Jun  7 12:35 ..
-rw-------  1 root root  411 Jun  7 12:35 openclaw_github
-rw-r--r--  1 root root   97 Jun  7 12:35 openclaw_github.pub
```

## Setup script

File:

```text
discord/setup_ssh.sh
```

Behavior:

1. Reads key from:
   ```text
   /data/.openclaw/ssh/openclaw_github
   ```
2. Restores runtime key to:
   ```text
   /root/.ssh/openclaw_github
   ```
3. Sets permissions:
   ```text
   /root/.ssh → 700
   /root/.ssh/openclaw_github → 600
   ```
4. Writes SSH config:
   ```text
   Host github.com
     IdentityFile /root/.ssh/openclaw_github
     StrictHostKeyChecking no
   ```
5. Adds GitHub host key using `ssh-keyscan`.
6. Prints:
   ```text
   SSH setup OK
   ```

Syntax verification:

```text
bash -n discord/setup_ssh.sh && echo "syntax OK"
syntax OK
```

## Bridge integration

File:

```text
discord/start_bridge.sh
```

Current startup flow:

```bash
#!/bin/bash
set -e
cd /data/workspace/openclaw-ai
bash discord/setup_ssh.sh
source discord/load_env.sh
exec discord/.venv/bin/python discord/bridge.py
```

This means every bridge start restores SSH config before launching Discord bridge.

## Restart simulation

Commands:

```bash
rm -f /root/.ssh/openclaw_github
rm -f /root/.ssh/config
ls -la /root/.ssh/
bash discord/setup_ssh.sh
ls -la /root/.ssh/openclaw_github
ssh -T git@github.com
git push origin main
```

Output:

```text
REMOVED
-rw-r--r-- root root 2484 known_hosts
drwx------ root root 4096 .ssh
SSH setup OK
RESTORED
-rw------- root root 411 openclaw_github
SSH_TEST
Hi LeeJMaiRap! You've successfully authenticated, but GitHub does not provide shell access.
PUSH_TEST
Everything up-to-date
```

## Security notes

Private key is not stored in the Git repo.

Private key is stored only in persistent OpenClaw state volume:

```text
/data/.openclaw/ssh/openclaw_github
```

Runtime copy is restored as needed:

```text
/root/.ssh/openclaw_github
```

Git remote uses SSH:

```text
git@github.com:LeeJMaiRap/openclaw-software.git
```

PAT is no longer required for container pushes.

## Final verdict

Sprint 10 succeeded.

GitHub SSH push now survives container restart because `start_bridge.sh` restores SSH key material from the persistent `/data/.openclaw` state volume before starting the bridge.
