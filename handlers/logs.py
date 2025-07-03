"""Logging utilities and handlers."""

from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Chat, User, Message, ChatMemberUpdated
from config import LOG_CHANNEL_ID

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

    @app.on_my_chat_member()
    async def member_updates(client: Client, update: ChatMemberUpdated):
        if update.new_chat_member.status == "kicked":
            await log_event(client, "Bot was kicked", update.chat)
        elif update.new_chat_member.status in {"member", "administrator"}:
            await log_event(client, "Bot was added", update.chat)
