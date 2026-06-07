#!/bin/bash
set -e
cd /data/workspace/openclaw-ai
bash discord/setup_ssh.sh
source discord/load_env.sh
exec discord/.venv/bin/python discord/bridge.py
