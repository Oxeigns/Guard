"""Logging utilities and handlers."""

import logging
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Chat, User, Message, ChatMemberUpdated
from config import LOG_CHANNEL_ID
from utils.errors import catch_errors

logger = logging.getLogger(__name__)


async def log_action_tracker(client: Client, chat: Chat, actor: User | None, action: str) -> None:
    """Send a formatted bot action log to the log channel."""
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if actor:
        user_line = f"👤 <a href=\"tg://user?id={actor.id}\">{actor.first_name}</a>"
        id_line = f"🆔 <code>{actor.id}</code>"
    else:
        user_line = "👤 Unknown"
        id_line = "🆔 <code>?</code>"

    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━",
        "📍 <b>BOT ACTION TRACKER</b>",
        user_line,
        id_line,
        f"🕒 <code>{time_str}</code>",
        "",
    ]

    if action == "removed":
        lines.extend([
            "🗑️ <i>Removed from Group</i>",
            f"Chat ID: <code>{chat.id}</code>",
            f"Chat Name: {chat.title or 'Private'}",
        ])
    elif action == "readded":
        lines.extend([
            "➕ <i>Re-added to Group</i>",
            f"By: {user_line if actor else 'Unknown'}",
        ])

    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    await client.send_message(LOG_CHANNEL_ID, "\n".join(lines))

async def log_event(client: Client, action: str, source: Chat | User):
    if isinstance(source, Chat):
        name = source.title or "Private"
        ident = f"🏷 {name}\n🆔 <code>{source.id}</code>"
    else:
        ident = f"<a href=\"tg://user?id={source.id}\">{source.first_name}</a>\n🆔 <code>{source.id}</code>"

    text = (
        f"<b>📘 Bot Log</b>\n"
        f"🔹 Action: {action}\n"
        f"{ident}\n"
        f"🕒 <code>{datetime.utcnow().isoformat()}</code>"
    )
    await client.send_message(LOG_CHANNEL_ID, text)


def init(app: Client) -> None:
    @app.on_message(filters.command("start") & filters.private)
    @catch_errors
    async def private_start(client: Client, message: Message):
        logger.debug("log private_start from %s", message.from_user.id)
        await log_event(client, "Bot started in private", message.from_user)

    @app.on_chat_member_updated()
    @catch_errors
    async def member_updates(client: Client, update: ChatMemberUpdated):
        logger.debug("chat member update in %s", update.chat.id)
        if not update.new_chat_member.user.is_self:
            return
        if update.new_chat_member.status == "kicked":
            await log_action_tracker(client, update.chat, update.from_user, "removed")
        elif update.new_chat_member.status in {"member", "administrator"}:
            await log_action_tracker(client, update.chat, update.from_user, "readded")
