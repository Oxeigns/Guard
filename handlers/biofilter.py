"""Bio link detection and progressive moderation."""

import logging
import re
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions

from utils.perms import is_admin
from utils.errors import catch_errors
from utils.db import (
    is_approved,
    increment_warning,
    reset_warning,
    get_bio_filter,
)

logger = logging.getLogger(__name__)

LINK_RE = re.compile(r"https?://\S+|t\.me/\S+|\w+\.\w{2,}", re.IGNORECASE)
MAX_BIO_LENGTH = 800


def contains_link(text: str) -> bool:
    return bool(LINK_RE.search(text))


def register(app: Client) -> None:
    @app.on_message(filters.group & filters.text)
    @catch_errors
    async def bio_filter(client: Client, message: Message):
        logger.debug("bio_filter check in %s from %s", message.chat.id, message.from_user.id if message.from_user else None)
        user = message.from_user
        if not user or user.is_bot:
            return
        if not await get_bio_filter(message.chat.id):
            return
        if await is_admin(client, message, user.id):
            return
        if await is_approved(message.chat.id, user.id):
            return

        # Fetch full user info to access bio
        user_full = await client.get_users(user.id)
        bio = user_full.bio
        if not bio:
            return
        if len(bio) <= MAX_BIO_LENGTH and not contains_link(bio):
            return

        await message.delete()
        count = await increment_warning(message.chat.id, user.id)
        if count == 1:
            warning = "⚠️ Warning 1"
        elif count == 2:
            warning = "⚠️ Warning 2"
        else:
            warning = "⛔ Final Warning"
            await client.restrict_chat_member(
                message.chat.id,
                user.id,
                ChatPermissions(),
            )
            await reset_warning(message.chat.id, user.id)
        await message.reply_text(warning, quote=True)

    @app.on_message(filters.new_chat_members)
    @catch_errors
    async def new_member_check(client: Client, message: Message):
        logger.debug("new_member_check in %s", message.chat.id)
        if not await get_bio_filter(message.chat.id):
            return
        for user in message.new_chat_members:
            if user.is_bot:
                continue
            if await is_admin(client, message, user.id):
                continue
            if await is_approved(message.chat.id, user.id):
                continue
            user_full = await client.get_users(user.id)
            bio = user_full.bio
            if not bio:
                continue
            if len(bio) <= MAX_BIO_LENGTH and not contains_link(bio):
                continue
            try:
                await message.delete()
            except Exception:
                await message.reply_text(
                    "❌ I can't delete messages. Please give me Delete rights.",
                    quote=True,
                )
            count = await increment_warning(message.chat.id, user.id)
            if count >= 3:
                await client.restrict_chat_member(message.chat.id, user.id, ChatPermissions())
                await reset_warning(message.chat.id, user.id)
                warning = "⛔ Final Warning"
            else:
                warning = f"⚠️ Warning {count}"
            await message.reply_text(warning, quote=True)

