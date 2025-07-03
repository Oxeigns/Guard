"""Logging utilities and handlers."""

from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Chat, User, Message, ChatMemberUpdated
from config import LOG_CHANNEL_ID


async def log_action_tracker(client: Client, chat: Chat, actor: User | None, action: str) -> None:
    """Send a formatted bot action log to the log channel."""
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if actor:
        user_line = f"👤 [{actor.first_name}](tg://user?id={actor.id})"
        id_line = f"🆔 `{actor.id}`"
    else:
        user_line = "👤 Unknown"
        id_line = "🆔 `?`"

    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━",
        "📍 **BOT ACTION TRACKER**",
        user_line,
        id_line,
        f"🕒 `{time_str}`",
        "",
    ]

    if action == "removed":
        lines.extend([
            "🗑️ *Removed from Group*",
            f"Chat ID: `{chat.id}`",
            f"Chat Name: {chat.title or 'Private'}",
        ])
    elif action == "readded":
        lines.extend([
            "➕ *Re-added to Group*",
            f"By: {user_line if actor else 'Unknown'}",
        ])

    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    await client.send_message(LOG_CHANNEL_ID, "\n".join(lines), parse_mode="Markdown")

async def log_event(client: Client, action: str, source: Chat | User):
    if isinstance(source, Chat):
        name = source.title or "Private"
        ident = f"🏷 {name}\n🆔 `{source.id}`"
    else:
        ident = f"[{source.first_name}](tg://user?id={source.id})\n🆔 `{source.id}`"

    text = (
        f"**📘 Bot Log**\n"
        f"🔹 Action: {action}\n"
        f"{ident}\n"
        f"🕒 `{datetime.utcnow().isoformat()}`"
    )
    await client.send_message(LOG_CHANNEL_ID, text, parse_mode="Markdown")


def register(app: Client):
    @app.on_message(filters.command("start") & filters.private)
    async def private_start(client: Client, message: Message):
        await log_event(client, "Bot started in private", message.from_user)

    @app.on_chat_member_updated()
    async def member_updates(client: Client, update: ChatMemberUpdated):
        if not update.new_chat_member.user.is_self:
            return
        if update.new_chat_member.status == "kicked":
            await log_action_tracker(client, update.chat, update.from_user, "removed")
        elif update.new_chat_member.status in {"member", "administrator"}:
            await log_action_tracker(client, update.chat, update.from_user, "readded")
