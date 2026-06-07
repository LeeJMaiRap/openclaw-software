# Sprint 10 Retrospective

## Summary

Sprint 10 made GitHub SSH push persistent across container restarts.

Status: ✅ Done
Closed: 2026-06-07 12:39 UTC

Main result:

```text
state volume SSH key → setup_ssh.sh restore → start_bridge.sh auto-run → git push works without PAT
```

## What shipped

### Persistent SSH key storage

Stored key in OpenClaw state volume:

```text
/data/.openclaw/ssh/openclaw_github
/data/.openclaw/ssh/openclaw_github.pub
```

Permissions:

```text
/data/.openclaw/ssh → 700
/data/.openclaw/ssh/openclaw_github → 600
```

### SSH restore script

Created:

```text
discord/setup_ssh.sh
```

The script:

- verifies persistent key exists
- creates `/root/.ssh`
- copies key into runtime path
- sets secure permissions
- writes GitHub SSH config
- refreshes GitHub known_hosts
- prints `SSH setup OK`

### Bridge startup integration

Updated:

```text
discord/start_bridge.sh
```

New flow:

```text
cd repo
setup SSH
load Discord env
exec bridge process
```

This guarantees SSH config is restored every time bridge starts.

## Verification

### Volume inspection

Mounts:

```text
/var/lib/docker/volumes/openclaw-software-state/_data -> /data/.openclaw
/var/lib/docker/volumes/openclaw-software-workspace/_data -> /data/workspace
/run/desktop/mnt/host/wsl/docker-desktop-bind-mounts/Ubuntu/docker.sock -> /var/run/docker.sock
```

Decision:

```text
Use /data/.openclaw for durable SSH state.
```

### Syntax checks

```text
bash -n discord/setup_ssh.sh && echo "syntax OK"
syntax OK

bash -n discord/start_bridge.sh && echo "syntax OK"
syntax OK
```

### Restart simulation

Removed runtime key/config:

```text
rm -f /root/.ssh/openclaw_github
rm -f /root/.ssh/config
```

Then restored via script:

```text
SSH setup OK
```

Restored key:

```text
-rw------- root root 411 openclaw_github
```

SSH test:

```text
Hi LeeJMaiRap! You've successfully authenticated, but GitHub does not provide shell access.
```

Push test:

```text
Everything up-to-date
```

## What worked

### `/data/.openclaw` is correct durable home

The state volume is separate from the Git workspace and survives container restart.

### Startup hook is enough

No systemd or Docker entrypoint change was needed for current setup. `start_bridge.sh` already controls bridge startup, so adding `bash discord/setup_ssh.sh` there solved the problem.

### PAT removed from normal flow

From now on, container Git pushes use SSH:

```text
git@github.com:LeeJMaiRap/openclaw-software.git
```

No PAT needed for regular commits/pushes.

## Risks / follow-ups

### Private key still exists in container state

This is intentional, but protect access to the Docker volume and host machine.

### `StrictHostKeyChecking no`

Current setup prioritizes reliability. A stricter future version can pin GitHub host keys and avoid disabling strict checking.

### `ssh-keyscan` appends repeatedly

`setup_ssh.sh` appends to `known_hosts` each run. It is harmless but can grow. Future improvement: deduplicate or rewrite known_hosts entry.

## Final verdict

Sprint 10 succeeded.

GitHub SSH push now survives simulated restart and works without PAT.
