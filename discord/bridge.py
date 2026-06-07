#!/usr/bin/env python3
"""Discord bridge for OpenClaw.

Sprint 7 behavior:
- Project commands create/list/archive Discord project categories.
- Project categories contain #leej, #workers, #results, #artifacts.
- !run in project #leej routes progress/results/artifacts to project channels.
- !run in legacy DISCORD_INPUT_CHANNEL_ID keeps Sprint 6 behavior.
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
import subprocess
import tempfile
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Final

import discord

try:
    from . import channel_manager, store
except ImportError:  # pragma: no cover - direct script execution fallback
    import channel_manager  # type: ignore
    import store  # type: ignore

WORKDIR: Final[Path] = Path(os.environ.get("OPENCLAW_PROJECT_DIR", "/data/workspace/openclaw-ai"))
LOG_PATH: Final[Path] = WORKDIR / "discord" / "bridge.log"
LOG_MAX_BYTES: Final[int] = 5 * 1024 * 1024
LOG_BACKUP_COUNT: Final[int] = 3
DISCORD_LIMIT: Final[int] = 2000
SAFE_TEXT_LIMIT: Final[int] = 1800
COMMAND_RE: Final[re.Pattern[str]] = re.compile(r'^!run\s+"(?P<request>.+)"\s*$', re.DOTALL)
PROJECT_CREATE_RE: Final[re.Pattern[str]] = re.compile(r"^!project\s+create\s+(?P<name>.+)$", re.DOTALL)
PROJECT_DONE_RE: Final[re.Pattern[str]] = re.compile(r"^!project\s+done\s+(?P<name>.+)$", re.DOTALL)
PROJECT_LIST_RE: Final[re.Pattern[str]] = re.compile(r"^!project\s+list\s*$")
PROJECT_RUN_ROLE: Final[str] = "leej"

logger = logging.getLogger("openclaw.discord.bridge")


def configure_logging() -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    handler = RotatingFileHandler(
        LOG_PATH,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    root.addHandler(handler)


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

async def resolve_channel(channel_id: int | str) -> discord.abc.Messageable:
    channel = client.get_channel(int(channel_id))
    if channel is None:
        channel = await client.fetch_channel(int(channel_id))
    if channel is None:
        raise RuntimeError(f"Cannot resolve channel: {channel_id}")
    if not isinstance(channel, discord.abc.Messageable):
        raise RuntimeError(f"Channel is not messageable: {channel_id}")
    return channel

async def get_output_channel() -> discord.abc.Messageable:
    return await resolve_channel(OUTPUT_CHANNEL_ID)

async def resolve_project_route(message: discord.Message) -> dict[str, Any] | None:
    project = channel_manager.get_project_by_channel(message.channel.id)
    if project is None:
        return None
    channels = project.get("channels") or {}
    return {
        "project": project,
        "role": project.get("role"),
        "workers": await resolve_channel(channels["workers"]),
        "results": await resolve_channel(channels["results"]),
        "artifacts": await resolve_channel(channels["artifacts"]),
    }

async def handle_project_create(message: discord.Message, project_name: str) -> None:
    if message.guild is None:
        return
    clean_name = channel_manager.sanitize_name(project_name)
    try:
        result = await channel_manager.create_project_category(message.guild, project_name)
    except Exception as exc:  # noqa: BLE001
        await message.channel.send(f"❌ Không tạo được project \"{clean_name}\": {type(exc).__name__}: {exc}")
        return

    if result.get("existing"):
        await message.channel.send(
            f"⚠️ Project \"{result['project']}\" đã tồn tại.\n"
            "Dùng channel #leej trong category đó để chạy `!run`."
        )
        return

    await message.channel.send(
        f"✅ Project \"{result['project']}\" đã tạo\n"
        "Category và channels đã sẵn sàng."
    )

async def handle_project_list(message: discord.Message) -> None:
    projects = store.list_projects()
    if not projects:
        await message.channel.send("Chưa có project active.")
        return

    lines = ["Projects active:"]
    for project in projects:
        channels = store.get_project_channels(str(project["name"]))
        status = "active"
        lines.append(
            f"- {project['name']} — {status} — category {project['category_id']} — "
            f"leej {channels.get('leej', 'missing')}"
        )
    await send_text_or_file(message.channel, "\n".join(lines), "openclaw-projects.md")

async def handle_project_done(message: discord.Message, project_name: str) -> None:
    if message.guild is None:
        return
    clean_name = channel_manager.sanitize_name(project_name)
    try:
        await channel_manager.archive_project(message.guild, project_name)
    except Exception as exc:  # noqa: BLE001
        await message.channel.send(f"❌ Không archive được project \"{clean_name}\": {type(exc).__name__}: {exc}")
        return
    await message.channel.send(f"✅ Project \"{clean_name}\" đã archive")

async def handle_run(message: discord.Message, request: str) -> None:
    project_route = await resolve_project_route(message)

    if project_route is None:
        if message.channel.id != INPUT_CHANNEL_ID:
            return
        workers_channel = message.channel
        results_channel = await get_output_channel()
        artifacts_channel = results_channel
        await message.channel.send("⚙️ Đang xử lý yêu cầu của bạn...")
    else:
        role = project_route["role"]
        project = project_route["project"]
        if role != PROJECT_RUN_ROLE:
            await message.channel.send("⚠️ Hãy chạy `!run` trong channel #leej của project này.")
            return
        workers_channel = project_route["workers"]
        results_channel = project_route["results"]
        artifacts_channel = project_route["artifacts"]
        await message.channel.send("⚙️ Đã nhận yêu cầu. Theo dõi progress trong #workers.")
        await workers_channel.send(f"⚙️ Project {project['name']}: bắt đầu pipeline\nRequest: {request}")

    try:
        result = await run_pipeline(request)
    except subprocess.TimeoutExpired:
        await results_channel.send("❌ Pipeline failed: timeout after 60 minutes")
        return
    except Exception as exc:  # noqa: BLE001 - bridge must report runtime failures clearly
        await results_channel.send(f"❌ Pipeline failed before start: {type(exc).__name__}: {exc}")
        return

    summary, report_path = build_summary(request, result)
    batch_id = extract_batch_id(result.stdout or "") or "unknown"

    if project_route is not None:
        await workers_channel.send(f"✅ Pipeline finished. Batch: {batch_id}. Exit code: {result.returncode}")

    await send_text_or_file(results_channel, summary, f"{batch_id}-discord-output.md")

    if report_path is not None:
        try:
            await artifacts_channel.send(
                f"📎 Pipeline report: {report_path.name}",
                file=discord.File(str(report_path), filename=report_path.name),
            )
        except Exception as exc:  # noqa: BLE001
            await results_channel.send(f"⚠️ Không attach được pipeline report: {type(exc).__name__}: {exc}")

@client.event
async def on_ready() -> None:
    logger.info("Logged in as %s", client.user)
    logger.info(
        "Bridge ready. Listening... guild=%s input=%s output=%s",
        GUILD_ID,
        INPUT_CHANNEL_ID,
        OUTPUT_CHANNEL_ID,
    )

@client.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return
    if message.guild is None or message.guild.id != GUILD_ID:
        return

    content = message.content.strip()

    project_create = PROJECT_CREATE_RE.match(content)
    if project_create:
        await handle_project_create(message, project_create.group("name").strip())
        return

    if PROJECT_LIST_RE.match(content):
        await handle_project_list(message)
        return

    project_done = PROJECT_DONE_RE.match(content)
    if project_done:
        await handle_project_done(message, project_done.group("name").strip())
        return

    run_match = COMMAND_RE.match(content)
    if run_match:
        await handle_run(message, run_match.group("request").strip())
        return

def main() -> None:
    configure_logging()
    if not WORKDIR.exists():
        raise ConfigError(f"Project directory does not exist: {WORKDIR}")
    store.init_db()
    logger.info(
        "discord-bridge starting | workdir=%s input=%s output=%s",
        WORKDIR,
        INPUT_CHANNEL_ID,
        OUTPUT_CHANNEL_ID,
    )
    client.run(TOKEN)

if __name__ == "__main__":
    main()
