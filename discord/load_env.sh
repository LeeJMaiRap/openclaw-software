#!/bin/bash
set -euo pipefail

ENV_FILE="${DISCORD_ENV_FILE:-discord/.env}"

if [ ! -f "$ENV_FILE" ]; then
  echo "missing env file: $ENV_FILE" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

required_vars=(
  DISCORD_BOT_TOKEN
  DISCORD_GUILD_ID
  DISCORD_INPUT_CHANNEL_ID
  DISCORD_OUTPUT_CHANNEL_ID
)

for name in "${required_vars[@]}"; do
  if [ -z "${!name:-}" ]; then
    echo "missing required env var: $name" >&2
    exit 1
  fi
done
