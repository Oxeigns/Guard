"""Message based moderation filters."""

import asyncio
import logging
import re
from contextlib import suppress

from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import (
    Message,
    ChatPermissions,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from utils.errors import catch_errors
from utils.perms import is_admin
from utils.db import (
    get_setting,
    get_bio_filter,
    increment_warning,
    reset_warning,
    is_approved,
    get_approval_mode,
)
from config import SUPPORT_CHAT_URL

logger = logging.getLogger(__name__)

# Regex to match typical web/telegram links. This is intentionally simple as
# we only need a coarse filter for moderation purposes.
LINK_RE = re.compile(
    r"(?:https?://\S+|tg://\S+|t\.me/\S+|telegram\.me/\S+|(?:\w+\.)+\w{2,})",
    re.IGNORECASE,
)
MAX_BIO_LENGTH = 800
SUPPORT_CHAT = SUPPORT_CHAT_URL


def contains_link(text: str) -> bool:
    return bool(LINK_RE.search(text or ""))


async def suppress_delete(message: Message):
    with suppress(Exception):
        await message.delete()


def build_warning(count: int, user, reason: str, is_final: bool = False):
    name = f"@{user.username}" if user.username else f"{user.first_name} ({user.id})"
    support_btn = InlineKeyboardButton("📨 Support", url=SUPPORT_CHAT)

    if is_final:
        msg = (
            f"🔇 <b>Final Warning for {name}</b>\n\n"
            f"{reason}\n"
            "You have been <b>muted</b>.\n"
            "Contact an admin or support to regain permissions."
        )
    else:
        msg = (
            f"⚠️ <b>Warning {count}/3 for {name}</b>\n\n"
            f"{reason}\n"
            "Fix this before you're muted."
        )

    return msg, InlineKeyboardMarkup([[support_btn]])


def register(app: Client) -> None:
    edited_messages: set[tuple[int, int]] = set()

    async def delete_later(chat_id: int, message_id: int, delay: int) -> None:
        await asyncio.sleep(max(delay, 0))
        try:
            await app.delete_messages(chat_id, message_id)
            logger.debug("Deleted %s/%s after %ss", chat_id, message_id, delay)
        except Exception as exc:
            logger.warning("Failed to delete %s/%s: %s", chat_id, message_id, exc)
        finally:
            edited_messages.discard((chat_id, message_id))

    async def schedule_auto_delete(
        chat_id: int, message_id: int, *, fallback: int | None = None
    ) -> None:
        delay_raw = await get_setting(chat_id, "autodelete_interval", "0")
        try:
            delay = int(delay_raw or 0)
        except (TypeError, ValueError):
            delay = 0
        if delay <= 0:
            if fallback is None:
                return
            delay = fallback
        logger.debug(
            "[AUTODELETE] schedule %s/%s after %ss", chat_id, message_id, delay
        )
        asyncio.create_task(delete_later(chat_id, message_id, delay))

    @app.on_message(filters.group & ~filters.service)
    @catch_errors
    async def moderate_message(client: Client, message: Message) -> None:
        """Main entry for all incoming group messages."""
        if not message.from_user or message.from_user.is_bot:
            return

        bot_id = (await client.get_me()).id
        if message.from_user.id == bot_id:
            return

        chat_id = message.chat.id
        user = message.from_user

        user_admin = bool(await is_admin(client, message, user.id))
        user_approved = bool(await is_approved(chat_id, user.id))

        if not user_admin and not user_approved and await get_approval_mode(chat_id):
            logger.debug("Unapproved user %s in %s", user.id, chat_id)
            await suppress_delete(message)
            await message.reply_text(
                "❌ You are not approved to speak here.",
                parse_mode=ParseMode.HTML,
                quote=True,
            )
            return

        text = message.text or message.caption or ""

        link_enabled = str(await get_setting(chat_id, "linkfilter", "0")) == "1"
        if text and link_enabled and not user_admin and not user_approved and contains_link(text):
            logger.debug("Link blocked from %s in %s", user.id, chat_id)
            await suppress_delete(message)
            count = await increment_warning(chat_id, user.id)
            reason = "You are not allowed to share links in this group."
            if count >= 3:
                await client.restrict_chat_member(chat_id, user.id, ChatPermissions())
                await reset_warning(chat_id, user.id)
            msg, kb = build_warning(count, user, reason, is_final=(count >= 3))
            await message.reply_text(msg, reply_markup=kb, parse_mode=ParseMode.HTML, quote=True)
            return

        bio_filter_enabled = bool(await get_bio_filter(chat_id))
        if bio_filter_enabled and not user_admin and not user_approved:
            try:
                user_info = await client.get_users(user.id)
                bio = getattr(user_info, "bio", "") or ""
            except Exception as exc:
                logger.debug("Bio fetch failed for %s: %s", user.id, exc)
                bio = ""
            if bio and (len(bio) > MAX_BIO_LENGTH or contains_link(bio)):
                logger.debug("Bio violation from %s in %s", user.id, chat_id)
                await suppress_delete(message)
                count = await increment_warning(chat_id, user.id)
                reason = "Your bio contains a link or is too long, which is not allowed."
                if count >= 3:
                    await client.restrict_chat_member(chat_id, user.id, ChatPermissions())
                    await reset_warning(chat_id, user.id)
                msg, kb = build_warning(count, user, reason, is_final=(count >= 3))
                await message.reply_text(msg, reply_markup=kb, parse_mode=ParseMode.HTML, quote=True)
                return

        if not user_admin and not user_approved:
            await schedule_auto_delete(chat_id, message.id)

    @app.on_edited_message(filters.group & ~filters.service)
    @catch_errors
    async def on_edit(client: Client, message: Message):
        if not message.from_user or message.from_user.is_bot:
            return
        bot_id = (await client.get_me()).id
        if message.from_user.id != bot_id:
            user = message.from_user
            user_admin = bool(await is_admin(client, message, user.id))
            user_approved = bool(await is_approved(message.chat.id, user.id))
            logger.debug(
                "[EDITMODE] %s %s admin=%s approved=%s",
                message.chat.id,
                message.id,
                user_admin,
                user_approved,
            )
            if user_admin or user_approved:
                return
            if str(await get_setting(message.chat.id, "editmode", "0")) != "1":
                return
            key = (message.chat.id, message.id)
            if key not in edited_messages:
                edited_messages.add(key)
                logger.debug("Deleting edited message %s/%s", message.chat.id, message.id)
                await schedule_auto_delete(message.chat.id, message.id, fallback=0)

    @app.on_message(filters.new_chat_members)
    @catch_errors
    async def check_new_member_bio(client: Client, message: Message):
        chat_id = message.chat.id
        bio_filter_enabled = await get_bio_filter(chat_id)
        logger.debug("[BIOFILTER] join %s enabled=%s", chat_id, bio_filter_enabled)
        if not bio_filter_enabled:
            return

        for user in message.new_chat_members:
            user_admin = bool(await is_admin(client, message, user.id))
            user_approved = bool(await is_approved(chat_id, user.id))
            if user.is_bot or user_admin or user_approved:
                continue
            try:
                user_info = await client.get_chat(user.id)
                bio = getattr(user_info, "bio", "")
            except Exception as exc:
                logger.debug("Failed to fetch bio for %s on join: %s", user.id, exc)
                continue
            has_link = contains_link(bio)
            if not bio or (len(bio) <= MAX_BIO_LENGTH and not has_link):
                continue

            logger.debug("[BIOFILTER] join bio %s: %s", user.id, bio)

            logger.debug("Bio link detected on join for %s in %s", user.id, chat_id)
            await suppress_delete(message)
            count = await increment_warning(chat_id, user.id)
            logger.debug("Warn %s in %s: count=%s", user.id, chat_id, count)
            reason = "Your bio contains a link or is too long, which is not allowed."
            if count >= 3:
                logger.debug("Muting %s in %s due to bio violation", user.id, chat_id)
                await client.restrict_chat_member(chat_id, user.id, ChatPermissions())
                await reset_warning(chat_id, user.id)
            msg, kb = build_warning(count, user, reason, is_final=(count >= 3))
            await message.reply_text(msg, reply_markup=kb, parse_mode=ParseMode.HTML, quote=True)
