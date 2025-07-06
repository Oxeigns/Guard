import asyncio
import logging
import re
from contextlib import suppress

from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, ChatPermissions

from utils.errors import catch_errors
from utils.db import (
    get_setting, get_bio_filter,
    increment_warning, reset_warning,
    is_approved, get_approval_mode,
)
from utils.perms import is_admin

logger = logging.getLogger(__name__)

LINK_RE = re.compile(
    r"(?:https?://\S+|tg://\S+|t\.me/\S+|telegram\.me/\S+|(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,})",
    re.IGNORECASE,
)
MAX_BIO_LENGTH = 800


def contains_link(text: str) -> bool:
    return bool(LINK_RE.search(text or ""))


async def suppress_delete(message: Message):
    with suppress(Exception):
        await message.delete()


def build_warning(count: int, user, reason: str, is_final: bool = False):
    name = f"@{user.username}" if user.username else f"{user.first_name} ({user.id})"
    msg = (
        f"🔇 <b>Final Warning for {name}</b>\n\n{reason}\nYou have been <b>muted</b>."
        if is_final
        else f"⚠️ <b>Warning {count}/3 for {name}</b>\n\n{reason}\nFix this before you're muted."
    )
    return msg, None


def register(app: Client) -> None:
    logger.info("✅ Registered: filters.py")

    edited_messages: set[tuple[int, int]] = set()

    async def delete_later(chat_id: int, msg_id: int, delay: int) -> None:
        await asyncio.sleep(delay)
        try:
            await app.delete_messages(chat_id, msg_id)
        except Exception as e:
            logger.warning("Failed to delete message %s/%s: %s", chat_id, msg_id, e)
        finally:
            edited_messages.discard((chat_id, msg_id))

    async def schedule_auto_delete(chat_id: int, msg_id: int, fallback: int | None = None):
        try:
            delay = int(await get_setting(chat_id, "autodelete_interval", "0") or 0)
        except (TypeError, ValueError):
            delay = 0
        if delay <= 0:
            delay = fallback or 0
        if delay > 0:
            asyncio.create_task(delete_later(chat_id, msg_id, delay))

    # Main message moderation
    @app.on_message(filters.group & ~filters.service, group=1)
    @catch_errors
    async def moderate_message(client: Client, message: Message) -> None:
        if not message.from_user or message.from_user.is_bot:
            return
        if (await client.get_me()).id == message.from_user.id:
            return

        chat_id = message.chat.id
        user = message.from_user

        is_admin_user = await is_admin(client, message, user.id)
        is_approved_user = await is_approved(chat_id, user.id)
        needs_filtering = not is_admin_user and not is_approved_user

        if needs_filtering:
            await schedule_auto_delete(chat_id, message.id)

        # Approval block
        if needs_filtering and await get_approval_mode(chat_id):
            await suppress_delete(message)
            await message.reply_text("❌ You are not approved to speak here.", quote=True)
            return

        # Content filters
        content = message.text or message.caption or ""
        if content:
            if needs_filtering and str(await get_setting(chat_id, "linkfilter", "0")) == "1" and contains_link(content):
                logger.debug("[FILTER] Link removed in %s from %s", chat_id, user.id)
                await handle_violation(client, message, user, chat_id, "You are not allowed to share links in this group.")
                return

            if needs_filtering and await get_bio_filter(chat_id):
                bio = getattr(user, "bio", "")
                if not bio:
                    try:
                        user_info = await client.get_chat(user.id)
                        bio = getattr(user_info, "bio", "")
                    except Exception:
                        bio = ""

                if bio and (len(bio) > MAX_BIO_LENGTH or contains_link(bio)):
                    logger.debug("[FILTER] Bio violation for %s in %s", user.id, chat_id)
                    await handle_violation(client, message, user, chat_id, "Your bio contains a link or is too long, which is not allowed.")
                    return

    async def handle_violation(client: Client, message: Message, user, chat_id: int, reason: str):
        logger.debug("[FILTER] Violation by %s in %s: %s", user.id, chat_id, reason)
        await suppress_delete(message)
        count = await increment_warning(chat_id, user.id)
        if count >= 3:
            await client.restrict_chat_member(chat_id, user.id, ChatPermissions())
            await reset_warning(chat_id, user.id)
        msg, _ = build_warning(count, user, reason, is_final=(count >= 3))
        await message.reply_text(msg, parse_mode=ParseMode.HTML, quote=True)

    # Edited message check
    @app.on_edited_message(filters.group & ~filters.service, group=1)
    @catch_errors
    async def on_edit(client: Client, message: Message):
        if not message.from_user or message.from_user.is_bot:
            return

        chat_id = message.chat.id
        user = message.from_user
        if await is_admin(client, message, user.id) or await is_approved(chat_id, user.id):
            return

        if str(await get_setting(chat_id, "editmode", "0")) != "1":
            return

        key = (chat_id, message.id)
        if key not in edited_messages:
            edited_messages.add(key)
            await schedule_auto_delete(chat_id, message.id, fallback=0)

    # New user bio check
    @app.on_message(filters.new_chat_members & filters.group, group=1)
    @catch_errors
    async def check_new_member_bio(client: Client, message: Message):
        chat_id = message.chat.id
        if not await get_bio_filter(chat_id):
            return

        for user in message.new_chat_members:
            if user.is_bot:
                continue
            if await is_admin(client, message, user.id) or await is_approved(chat_id, user.id):
                continue

            bio = getattr(user, "bio", "")
            if not bio:
                try:
                    user_info = await client.get_chat(user.id)
                    bio = getattr(user_info, "bio", "")
                except Exception:
                    continue

            if bio and (len(bio) > MAX_BIO_LENGTH or contains_link(bio)):
                logger.debug("[FILTER] New member bio violation %s in %s", user.id, chat_id)
                await suppress_delete(message)
                count = await increment_warning(chat_id, user.id)
                if count >= 3:
                    await client.restrict_chat_member(chat_id, user.id, ChatPermissions())
                    await reset_warning(chat_id, user.id)
                msg, _ = build_warning(count, user, "Your bio contains a link or is too long, which is not allowed.", is_final=(count >= 3))
                await message.reply_text(msg, parse_mode=ParseMode.HTML, quote=True)
