#!/usr/bin/env python3
"""Sprint 6 Discord bridge for OpenClaw.

MVP behavior:
- Listen for !run "<request>" in DISCORD_INPUT_CHANNEL_ID.
- Run `python3 leej/run.py <request>` in /data/workspace/openclaw-ai.
- Post pipeline result to DISCORD_OUTPUT_CHANNEL_ID.
- Attach output as markdown if Discord message would exceed 2000 chars.
"""

from __future__ import annotations

import asyncio
import os
import re
import shlex
import subprocess
import tempfile
from pathlib import Path
from typing import Final

import discord

WORKDIR: Final[Path] = Path(os.environ.get("OPENCLAW_PROJECT_DIR", "/data/workspace/openclaw-ai"))
DISCORD_LIMIT: Final[int] = 2000
SAFE_TEXT_LIMIT: Final[int] = 1800
COMMAND_RE: Final[re.Pattern[str]] = re.compile(r'^!run\s+"(?P<request>.+)"\s*$', re.DOTALL)


class ConfigError(RuntimeError):
    pass


def required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ConfigError(f"Missing required environment variable: {name}")
    return value


TOKEN = required_env("DISCORD_BOT_TOKEN")
GUILD_ID = int(required_env("DISCORD_GUILD_ID"))
INPUT_CHANNEL_ID = int(required_env("DISCORD_INPUT_CHANNEL_ID"))
OUTPUT_CHANNEL_ID = int(required_env("DISCORD_OUTPUT_CHANNEL_ID"))


intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True
client = discord.Client(intents=intents)


async def run_pipeline(request: str) -> subprocess.CompletedProcess[str]:
    cmd = ["python3", "leej/run.py", request]
    return await asyncio.to_thread(
        subprocess.run,
        cmd,
        cwd=str(WORKDIR),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=60 * 60,
    )


def extract_batch_id(output: str) -> str | None:
    patterns = (
        r"Batch\s+(B-\d+)",
        r"Batch:\s*(B-\d+)",
        r"✅\s*Batch\s+(B-\d+)",
    )
    for pattern in patterns:
        match = re.search(pattern, output)
        if match:
            return match.group(1)
    return None


def find_pipeline_report(batch_id: str | None) -> Path | None:
    if not batch_id:
        return None
    candidate = WORKDIR / "vaults" / "openclaw-ai" / "03-logs" / f"{batch_id}-pipeline.md"
    if candidate.exists():
        return candidate
    return None


def build_summary(request: str, result: subprocess.CompletedProcess[str]) -> tuple[str, Path | None]:
    output = result.stdout or ""
    batch_id = extract_batch_id(output)
    report_path = find_pipeline_report(batch_id)
    status = "✅ Pipeline complete" if result.returncode == 0 else "❌ Pipeline failed"

    lines = [
        status,
        f"Request: {request}",
    ]
    if batch_id:
        lines.append(f"Batch: {batch_id}")
    lines.extend(
        [
            f"Exit code: {result.returncode}",
            "",
            "Output:",
            output.strip() or "(no output)",
        ]
    )
    return "\n".join(lines), report_path


async def send_text_or_file(channel: discord.abc.Messageable, content: str, filename: str) -> None:
    if len(content) <= SAFE_TEXT_LIMIT:
        await channel.send(content)
        return

    with tempfile.NamedTemporaryFile("w", suffix=".md", prefix="openclaw-", delete=False, encoding="utf-8") as handle:
        handle.write(content)
        temp_path = Path(handle.name)

    try:
        await channel.send(
            "📎 Output dài hơn Discord limit. Đính kèm file kết quả.",
            file=discord.File(str(temp_path), filename=filename),
        )
    finally:
        temp_path.unlink(missing_ok=True)


async def get_output_channel() -> discord.abc.Messageable:
    channel = client.get_channel(OUTPUT_CHANNEL_ID)
    if channel is None:
        channel = await client.fetch_channel(OUTPUT_CHANNEL_ID)
    if channel is None:
        raise RuntimeError(f"Cannot resolve output channel: {OUTPUT_CHANNEL_ID}")
    return channel


@client.event
async def on_ready() -> None:
    print(f"Logged in as {client.user}", flush=True)
    print(
        "Bridge ready. Listening... "
        f"guild={GUILD_ID} input={INPUT_CHANNEL_ID} output={OUTPUT_CHANNEL_ID}",
        flush=True,
    )


@client.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return
    if message.guild is None or message.guild.id != GUILD_ID:
        return
    if message.channel.id != INPUT_CHANNEL_ID:
        return

    match = COMMAND_RE.match(message.content.strip())
    if not match:
        return

    request = match.group("request").strip()
    output_channel = await get_output_channel()
    await message.channel.send("⚙️ Đang xử lý yêu cầu của bạn...")

    try:
        result = await run_pipeline(request)
    except subprocess.TimeoutExpired:
        await output_channel.send("❌ Pipeline failed: timeout after 60 minutes")
        return
    except Exception as exc:  # noqa: BLE001 - bridge must report runtime failures clearly
        await output_channel.send(f"❌ Pipeline failed before start: {type(exc).__name__}: {exc}")
        return

    summary, report_path = build_summary(request, result)
    batch_id = extract_batch_id(result.stdout or "") or "unknown"
    await send_text_or_file(output_channel, summary, f"{batch_id}-discord-output.md")

    if report_path is not None:
        try:
            await output_channel.send(
                f"📎 Pipeline report: {report_path.name}",
                file=discord.File(str(report_path), filename=report_path.name),
            )
        except Exception as exc:  # noqa: BLE001
            await output_channel.send(f"⚠️ Không attach được pipeline report: {type(exc).__name__}: {exc}")


def main() -> None:
    if not WORKDIR.exists():
        raise ConfigError(f"Project directory does not exist: {WORKDIR}")
    print(
        "discord-bridge starting | "
        f"workdir={WORKDIR} input={INPUT_CHANNEL_ID} output={OUTPUT_CHANNEL_ID}",
        flush=True,
    )
    client.run(TOKEN)


if __name__ == "__main__":
    main()
