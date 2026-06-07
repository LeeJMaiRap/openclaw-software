#!/bin/bash
set -e
cd /data/workspace/openclaw-ai
source discord/load_env.sh
exec discord/.venv/bin/python discord/bridge.py
