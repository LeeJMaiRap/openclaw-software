#!/bin/bash
set -e

PROJECT_DIR="/data/workspace/openclaw-ai"
LOG_FILE="$PROJECT_DIR/discord/healthcheck.log"
START_SCRIPT="$PROJECT_DIR/discord/start_bridge.sh"

cd "$PROJECT_DIR"

log() {
  printf '%s %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$*" >> "$LOG_FILE"
}

find_bridge_pid() {
  for cmdline in /proc/[0-9]*/cmdline; do
    [ -r "$cmdline" ] || continue
    pid="${cmdline#/proc/}"
    pid="${pid%/cmdline}"
    comm="$(cat "/proc/$pid/comm" 2>/dev/null || true)"
    cmd="$(tr '\000' ' ' < "$cmdline" 2>/dev/null || true)"

    case "$comm:$cmd" in
      python*:*"discord/bridge.py"*)
        printf '%s\n' "$pid"
        return 0
        ;;
    esac
  done
  return 1
}

pid="$(find_bridge_pid || true)"
if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
  log "bridge OK PID=$pid"
  exit 0
fi

log "bridge down, restarting"
nohup "$START_SCRIPT" >/dev/null 2>&1 &
new_pid="$!"
log "bridge restarted PID=$new_pid"
exit 0
