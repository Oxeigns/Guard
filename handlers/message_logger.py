"""Enhanced logging for all incoming messages, with context awareness."""

import logging
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.types import Message

from utils.errors import catch_errors
from utils.db import save_group_meta

logger = logging.getLogger(__name__)

def register(app: Client) -> None:

    @app.on_message(filters.all, group=-1)
    @catch_errors
    async def log_messages(client: Client, message: Message):
        user = message.from_user
        chat = message.chat

        user_str = f"{user.first_name} [{user.id}]" if user else "Unknown User"
        chat_str = f"{chat.title} [{chat.id}]" if chat.title else f"Private [{chat.id}]"

        content = message.text or message.caption or ""
        content_preview = content[:80] + "..." if len(content) > 80 else content

        kind = "Media" if message.media else "Text"

        logger.info(
            f"[📨 LOG] [{kind}] Chat: {chat_str} | From: {user_str} | Msg: {content_preview or '<empty>'}"
        )

        if chat.type != ChatType.PRIVATE:
            owner_id = 0
            try:
                admins = await client.get_chat_administrators(chat.id)
                for adm in admins:
                    if adm.status == ChatMemberStatus.OWNER:
                        owner_id = adm.user.id
                        break
            except Exception as e:
                logger.debug("Failed to fetch administrators: %s", e)
            photo_id = chat.photo.big_file_id if chat.photo else None
            await save_group_meta(chat.id, chat.title or "", owner_id, photo_id)

