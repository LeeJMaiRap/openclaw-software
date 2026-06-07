#!/bin/bash
set -e
SSH_KEY_SRC=/data/.openclaw/ssh/openclaw_github
SSH_DIR=/root/.ssh

if [ ! -f "$SSH_KEY_SRC" ]; then
  echo "SSH key not found at $SSH_KEY_SRC"
  exit 1
fi

mkdir -p "$SSH_DIR"
chmod 700 "$SSH_DIR"
cp "$SSH_KEY_SRC" "$SSH_DIR/openclaw_github"
chmod 600 "$SSH_DIR/openclaw_github"

cat > "$SSH_DIR/config" << 'CONFIG_EOF'
Host github.com
  IdentityFile /root/.ssh/openclaw_github
  StrictHostKeyChecking no
CONFIG_EOF

ssh-keyscan github.com >> "$SSH_DIR/known_hosts" 2>/dev/null
echo "SSH setup OK"
