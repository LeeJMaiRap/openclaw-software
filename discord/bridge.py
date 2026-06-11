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
import json
import logging
import os
import re
import subprocess
import tempfile
from datetime import datetime, timezone
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
FIX_RE: Final[re.Pattern[str]] = re.compile(r'^!fix\s+(?P<task_id>TASK-\d+)\s+"(?P<description>.+)"\s*$', re.DOTALL)
PROJECT_RUN_ROLE: Final[str] = "leej"
FIX_REQUEST_DIR: Final[Path] = WORKDIR / "vaults" / "openclaw-ai" / "03-logs" / "fix-requests"
OUTPUT_DIR: Final[Path] = WORKDIR / "vaults" / "openclaw-ai" / "02-outputs"
TASK_DIR: Final[Path] = WORKDIR / "tasks"
WORKER_MODEL_BY_NAME: Final[dict[str, str]] = {
    "worker-code": "gpt-gmn-token-tunel/cx/gpt-5.5",
    "worker-hermes": "gpt-gmn-token-tunel/cx/gpt-5.4",
    "worker-test": "gpt-gmn-token-tunel/cx/gpt-5.5",
}
WORKER_ROLE_BY_TASK_WORKER: Final[dict[str, str]] = {
    "claude-cli": "worker-code",
    "codex-cli": "worker-code",
    "hermes": "worker-hermes",
}

logger = logging.getLogger("openclaw.discord.bridge")

def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


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

async def run_pipeline(
    request: str,
    project_id: int | str | None = None,
    project_name: str | None = None,
) -> subprocess.CompletedProcess[str]:
    cmd = ["python3", "leej/run.py", "--auto-pr", request]
    env = os.environ.copy()
    if project_id is not None:
        env["OPENCLAW_DISCORD_PROJECT_ID"] = str(project_id)
    if project_name is not None:
        env["OPENCLAW_DISCORD_PROJECT_NAME"] = project_name
    return await asyncio.to_thread(
        subprocess.run,
        cmd,
        cwd=str(WORKDIR),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=60 * 60,
    )

def build_worker_bootstrap_prompt(project_name: str, worker_name: str) -> str:
    output_dir = WORKDIR / "vaults" / "openclaw-ai" / "02-outputs"
    done_log_dir = WORKDIR / "vaults" / "openclaw-ai" / "03-logs"
    return (
        f"Bạn là Worker {worker_name} của project {project_name}.\n"
        "Chờ task từ LeeJ Agent.\n"
        "Khi nhận task, thực hiện đầy đủ và báo cáo kết quả.\n"
        "Ghi output vào đường dẫn được chỉ định trong task.\n"
        "\n"
        "IMPORTANT — ABSOLUTE PATHS:\n"
        f"Workspace root: {WORKDIR}/\n"
        f"Output files:   {output_dir}/\n"
        f"Done logs:      {done_log_dir}/\n"
        f"Source code:    {WORKDIR}/\n"
        "NEVER write to: /data/workspace/ (wrong root)\n"
        "NEVER use relative paths.\n"
        f"ALWAYS use full absolute paths starting with {WORKDIR}/\n"
        "Không tự kết thúc."
    )

async def bootstrap_worker_session(project_name: str, worker_name: str, session_key: str) -> subprocess.CompletedProcess[str]:
    model = WORKER_MODEL_BY_NAME[worker_name]
    prompt = build_worker_bootstrap_prompt(project_name, worker_name)
    cmd = [
        "openclaw",
        "cron",
        "add",
        "--name",
        f"bootstrap-{session_key}",
        "--at",
        "+1s",
        "--session-key",
        session_key,
        "--model",
        model,
        "--thinking",
        "off",
        "--message",
        prompt,
        "--no-deliver",
        "--timeout-seconds",
        "120",
    ]
    result = await asyncio.to_thread(
        subprocess.run,
        cmd,
        cwd=str(WORKDIR),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=120,
    )
    logger.info(
        "worker bootstrap cron add | worker=%s session_key=%s returncode=%s output=%s",
        worker_name,
        session_key,
        result.returncode,
        result.stdout.strip(),
    )
    return result

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

def load_task(task_id: str) -> dict[str, Any]:
    path = TASK_DIR / f"{task_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"task file not found: {path.relative_to(WORKDIR)}")
    return json.loads(path.read_text(encoding="utf-8"))

def worker_role_for_task(task: dict[str, Any]) -> str:
    worker = str(task.get("worker", "")).strip()
    role = WORKER_ROLE_BY_TASK_WORKER.get(worker)
    if role is None:
        raise KeyError(f"no worker role mapping for task worker: {worker}")
    return role

def output_excerpt(task_id: str, limit: int = 1200) -> str:
    path = OUTPUT_DIR / f"{task_id}-output.md"
    if not path.exists():
        return "(no current output file)"
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "\n...(truncated)"

def build_fix_worker_message(task_id: str, fix_description: str) -> str:
    output_path = OUTPUT_DIR / f"{task_id}-output.md"
    done_log_path = WORKDIR / "vaults" / "openclaw-ai" / "03-logs" / f"{task_id}-done.md"
    return (
        f"[FIX REQUEST] {task_id}\n"
        f"Fix description: {fix_description}\n\n"
        "IMPORTANT PATHS:\n"
        f"- Current output: {output_path}\n"
        "- Write fixed output to SAME path (overwrite)\n"
        f"- Write done log to: {done_log_path}\n"
        "- NEVER write to /data/workspace/ directly\n"
        "- NEVER use relative paths\n\n"
        f"Current output content:\n{output_excerpt(task_id)}\n\n"
        "Vui lòng fix và ghi output mới vào đúng absolute path ở trên."
    )

def write_fix_request(
    task_id: str,
    fix_description: str,
    project_id: int,
    worker_role: str,
    worker_session_key: str,
) -> Path:
    FIX_REQUEST_DIR.mkdir(parents=True, exist_ok=True)
    path = FIX_REQUEST_DIR / f"{task_id}-fix.json"
    payload = {
        "task_id": task_id,
        "fix_description": fix_description,
        "requested_at": utc_now(),
        "status": "pending",
        "project_id": project_id,
        "worker_role": worker_role,
        "worker_session_key": worker_session_key,
        "message": build_fix_worker_message(task_id, fix_description),
    }
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)
    return path

def infer_project_batch_id(project_id: int) -> str | None:
    tasks = store.list_tasks_by_project(project_id)
    if tasks:
        return str(tasks[-1]["batch_id"])

    marker = f"agent:software:project-{project_id}-"
    candidates: list[tuple[float, str]] = []
    for path in (WORKDIR / "vaults" / "openclaw-ai" / "03-logs").glob("B-*-runtime-actions.json"):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        if marker not in text:
            continue
        match = re.match(r"(B-\d+)-runtime-actions\.json$", path.name)
        if match:
            candidates.append((path.stat().st_mtime, match.group(1)))
    if not candidates:
        return None
    return sorted(candidates)[-1][1]

async def run_checker_batch(batch_id: str) -> subprocess.CompletedProcess[str]:
    return await asyncio.to_thread(
        subprocess.run,
        ["python3", "leej/checker.py", "--batch", batch_id],
        cwd=str(WORKDIR),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=20 * 60,
    )

def extract_pr_urls(output: str) -> list[str]:
    urls = re.findall(r"https://github\.com/[^\s)]+/pull/\d+", output)
    seen: set[str] = set()
    unique: list[str] = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique.append(url)
    return unique


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

    project = store.get_project(str(result["project"]))
    if project is None:
        await message.channel.send(f"❌ Project \"{result['project']}\" đã tạo channel nhưng thiếu SQLite mapping.")
        return

    worker_channel_ids = result.get("worker_channels") or {}
    worker_errors: list[str] = []
    for worker_name, channel_id in worker_channel_ids.items():
        session_key = f"agent:software:project-{project['id']}-{worker_name}"
        try:
            store.create_worker(int(project["id"]), worker_name, str(channel_id), session_key)
            spawn_result = await bootstrap_worker_session(str(result["project"]), worker_name, session_key)
        except Exception as exc:  # noqa: BLE001
            worker_errors.append(f"{worker_name}: {type(exc).__name__}: {exc}")
            continue
        if spawn_result.returncode != 0:
            worker_errors.append(f"{worker_name}: cron bootstrap failed: {spawn_result.stdout.strip()}")

    if worker_errors:
        await message.channel.send(
            f"⚠️ Project \"{result['project']}\" đã tạo, nhưng worker session bootstrap lỗi:\n"
            + "\n".join(f"- {error}" for error in worker_errors)
        )
        return

    await message.channel.send(
        f"✅ Project \"{result['project']}\" đã tạo\n"
        "Workers: worker-code, worker-hermes, worker-test\n"
        "Sessions: ready"
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
    project = store.get_project(clean_name)
    if project is None:
        await message.channel.send(f"❌ Không tìm thấy project \"{clean_name}\".")
        return

    channels = store.get_project_channels(int(project["id"]))
    results_channel = await resolve_channel(channels["results"])
    batch_id = project.get("batch_id") or infer_project_batch_id(int(project["id"]))
    if not batch_id:
        pass
    else:
        store.update_project_batch_id(int(project["id"]), str(batch_id))

    summary_lines = [f"Project {clean_name} — tổng kết"]
    if batch_id:
        try:
            result = await run_checker_batch(str(batch_id))
            summary_lines.append(f"Batch: {batch_id}")
            summary_lines.append(result.stdout.strip() or "(checker no output)")
        except Exception as exc:  # noqa: BLE001
            summary_lines.append(f"Batch: {batch_id}")
            summary_lines.append(f"Checker failed: {type(exc).__name__}: {exc}")
    else:
        summary_lines.append("Batch: unknown")
        summary_lines.append("Tasks: unknown — project has no batch_id")

    await send_text_or_file(results_channel, "\n".join(summary_lines), f"{clean_name}-done-summary.md")

    try:
        await channel_manager.archive_project(message.guild, project_name)
    except Exception as exc:  # noqa: BLE001
        await message.channel.send(f"❌ Không archive được project \"{clean_name}\": {type(exc).__name__}: {exc}")
        return

    for worker in store.list_workers(int(project["id"])):
        store.update_worker_status(str(worker["name"]), int(project["id"]), "archived")

    await message.channel.send(
        f"✅ Project \"{clean_name}\" đã đóng.\n"
        "Category archived. Sessions closed."
    )

async def handle_fix(message: discord.Message, task_id: str, fix_description: str) -> None:
    project_route = await resolve_project_route(message)
    if project_route is None:
        await message.channel.send("⚠️ Hãy chạy `!fix` trong channel #leej của project.")
        return
    if project_route["role"] != PROJECT_RUN_ROLE:
        await message.channel.send("⚠️ Hãy chạy `!fix` trong channel #leej của project này.")
        return

    project = project_route["project"]
    workers_channel = project_route["workers"]
    try:
        task = load_task(task_id)
        worker_role = worker_role_for_task(task)
        worker = store.get_worker(worker_role, int(project["id"]))
        if worker is None:
            raise KeyError(f"worker not found: {worker_role}")
        request_path = write_fix_request(
            task_id,
            fix_description,
            int(project["id"]),
            worker_role,
            str(worker["session_key"]),
        )
    except Exception as exc:  # noqa: BLE001
        await message.channel.send(f"❌ Không ghi được fix request {task_id}: {type(exc).__name__}: {exc}")
        return

    await message.channel.send(
        f"📝 Fix request {task_id} đã ghi.\n"
        "Nhắn LeeJ 'xử lý fix requests' để tiến hành."
    )
    await workers_channel.send(f"⏳ {task_id}: fix request pending")
    logger.info(
        "fix request queued | task=%s project=%s worker=%s path=%s",
        task_id,
        project["name"],
        worker_role,
        request_path,
    )

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
        result = await run_pipeline(
            request,
            project["id"] if project_route is not None else None,
            project["name"] if project_route is not None else None,
        )
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

    pr_urls = extract_pr_urls(result.stdout or "")
    if pr_urls:
        if len(pr_urls) == 1:
            await results_channel.send(f"🔗 PR tạo tự động: {pr_urls[0]}")
        else:
            text = "\n".join(f"- {url}" for url in pr_urls)
            await artifacts_channel.send(f"🔗 PR tạo tự động:\n{text}")

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

    fix_match = FIX_RE.match(content)
    if fix_match:
        await handle_fix(
            message,
            fix_match.group("task_id").strip(),
            fix_match.group("description").strip(),
        )
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
