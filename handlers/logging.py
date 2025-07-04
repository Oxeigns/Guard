"""Enhanced logging for all incoming messages, with context awareness."""

import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.errors import catch_errors

logger = logging.getLogger(__name__)


def register(app: Client) -> None:
    @app.on_message(filters.all, group=-1)
    @catch_errors
    async def log_messages(client: Client, message: Message):
        user = message.from_user
        chat = message.chat

        # Format user info
        if user:
            name = user.first_name or "NoName"
            user_str = f"{name} [{user.id}]"
        else:
            user_str = "❓ Unknown User"

        # Format chat info
        if chat.type == "private":
            chat_str = f"🕵️ Private Chat [{chat.id}]"
        elif chat.title:
            chat_str = f"{chat.title} [{chat.id}]"
        else:
            chat_str = f"Chat [{chat.id}]"

        # Extract and trim message content
        content = message.text or message.caption or ""
        preview = (content[:80] + "...") if len(content) > 80 else content
        preview = preview.strip() or "<empty>"

        # Detect message type
        kind = "Unknown"
        if message.media:
            kind = message.media.value  # safer than .name
        elif content:
            kind = "Text"

        logger.info(
            f"[📨 MESSAGE] [{kind}] in {chat_str} | From: {user_str} | Content: {preview}"
        )
