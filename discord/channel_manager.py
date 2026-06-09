from __future__ import annotations

import re
from typing import Any

import discord

try:
    from . import store
except ImportError:  # pragma: no cover - direct script/import fallback
    import store  # type: ignore

CHANNEL_ROLES = ("leej", "workers", "results", "artifacts")
WORKER_ROLES = ("worker-code", "worker-hermes", "worker-test")
MAX_DISCORD_NAME_LEN = 100
MAX_CHANNELS_PER_CATEGORY = 50
DONE_PREFIX = "[done] "


def sanitize_name(name: str, fallback: str = "project") -> str:
    cleaned = name.strip().lower()
    cleaned = re.sub(r"[\s_]+", "-", cleaned)
    cleaned = re.sub(r"[^a-z0-9-]", "", cleaned)
    cleaned = re.sub(r"-+", "-", cleaned).strip("-")
    if not cleaned:
        cleaned = fallback
    return cleaned[:MAX_DISCORD_NAME_LEN].strip("-") or fallback


def category_channel_count(category: discord.CategoryChannel) -> int:
    return len(getattr(category, "channels", []) or [])


def ensure_category_capacity(category: discord.CategoryChannel, new_channels: int) -> None:
    if category_channel_count(category) + new_channels > MAX_CHANNELS_PER_CATEGORY:
        raise ValueError(
            f"category would exceed Discord limit: {MAX_CHANNELS_PER_CATEGORY} channels"
        )


async def create_project_category(guild: discord.Guild, project_name: str) -> dict[str, Any]:
    project_key = sanitize_name(project_name)
    existing = store.get_project(project_key)
    if existing is not None:
        channels = store.get_project_channels(project_key)
        return {
            "project": existing["name"],
            "category_id": str(existing["category_id"]),
            "channels": channels,
            "existing": True,
        }

    category = await guild.create_category(project_key)
    ensure_category_capacity(category, len(CHANNEL_ROLES) + len(WORKER_ROLES))

    channel_ids: dict[str, str] = {}
    worker_channel_ids: dict[str, str] = {}
    try:
        for role in CHANNEL_ROLES:
            channel_name = sanitize_name(role)
            channel = await guild.create_text_channel(channel_name, category=category)
            channel_ids[role] = str(channel.id)

        for role in WORKER_ROLES:
            channel_name = sanitize_name(role)
            channel = await guild.create_text_channel(channel_name, category=category)
            worker_channel_ids[role] = str(channel.id)

        store.create_project(project_key, str(category.id), channel_ids)
        return {
            "project": project_key,
            "category_id": str(category.id),
            "channels": channel_ids,
            "worker_channels": worker_channel_ids,
            "existing": False,
        }
    except Exception:
        # Best effort cleanup if mapping write/channel creation fails during initial create.
        for channel in list(getattr(category, "channels", []) or []):
            try:
                await channel.delete(reason="OpenClaw project create failed")
            except Exception:
                pass
        try:
            await category.delete(reason="OpenClaw project create failed")
        except Exception:
            pass
        raise


def get_project_by_channel(channel_id: int | str) -> dict[str, Any] | None:
    row = store.get_project_by_channel_id(str(channel_id))
    if row is None:
        return None
    # Confirm by category lookup so caller gets canonical project fields.
    project = store.get_project_by_category_id(str(row["category_id"]))
    if project is None:
        return None
    project["role"] = row.get("role")
    project["channel_id"] = str(channel_id)
    project["channels"] = store.get_project_channels(str(project["name"]))
    return project


async def fetch_channel(guild: discord.Guild, channel_id: str) -> discord.abc.GuildChannel | None:
    channel = guild.get_channel(int(channel_id))
    if channel is not None:
        return channel
    try:
        fetched = await guild.fetch_channel(int(channel_id))
    except discord.NotFound:
        return None
    if isinstance(fetched, discord.abc.GuildChannel):
        return fetched
    return None


async def archive_project(guild: discord.Guild, project_name: str) -> dict[str, Any]:
    project_key = sanitize_name(project_name)
    project = store.get_project(project_key)
    if project is None:
        raise KeyError(f"project not found: {project_key}")

    category = await fetch_channel(guild, str(project["category_id"]))
    if category is None or not isinstance(category, discord.CategoryChannel):
        raise KeyError(f"category not found: {project['category_id']}")

    done_name = sanitize_name(project_key)
    if not category.name.startswith(DONE_PREFIX):
        await category.edit(name=f"{DONE_PREFIX}{done_name}"[:MAX_DISCORD_NAME_LEN])

    overwrite = discord.PermissionOverwrite(send_messages=False)
    locked_channels: list[str] = []
    channels = store.get_project_channels(project_key)
    for role, channel_id in channels.items():
        channel = await fetch_channel(guild, channel_id)
        if channel is None:
            continue
        if hasattr(channel, "set_permissions"):
            await channel.set_permissions(
                guild.default_role,
                overwrite=overwrite,
                reason="OpenClaw project archived",
            )
            locked_channels.append(role)

    return {
        "project": project_key,
        "category_id": str(project["category_id"]),
        "archived_name": f"{DONE_PREFIX}{done_name}"[:MAX_DISCORD_NAME_LEN],
        "locked_channels": locked_channels,
    }
