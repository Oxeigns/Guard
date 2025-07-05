import asyncio
import logging
import re
from contextlib import suppress

from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton

from utils.db import (
    get_setting,
    get_bio_filter,
    increment_warning,
    reset_warning,
    is_approved,
    get_approval_mode,
)
from utils.perms import is_admin

logger = logging.getLogger(__name__)

LINK_RE = re.compile(r"(?:https?://\S+|tg://\S+|t\.me/\S+|telegram\.me/\S+|(?:\w+\.)+\w{2,})", re.IGNORECASE)
MAX_BIO_LENGTH = 800


def contains_link(text: str) -> bool:
    return bool(LINK_RE.search(text or ""))


async def suppress_delete(message: Message):
    with suppress(Exception):
        await message.delete()


def build_warning(count: int, user, reason: str, is_final: bool = False):
    name = f"@{user.username}" if user.username else f"{user.first_name} ({user.id})"
    btn = InlineKeyboardButton("📨 Support", url="https://t.me/botsyard")
    msg = (
        f"🔇 <b>Final Warning for {name}</b>\n\n{reason}\nYou have been <b>muted</b>." if is_final
        else f"⚠️ <b>Warning {count}/3 for {name}</b>\n\n{reason}\nFix this before you're muted."
    )
    return msg, InlineKeyboardMarkup([[btn]])


def register(app: Client) -> None:
    edited_messages: set[tuple[int, int]] = set()

    async def delete_later(chat_id: int, msg_id: int, delay: int) -> None:
        await asyncio.sleep(max(delay, 0))
        try:
            await app.delete_messages(chat_id, msg_id)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to delete %s/%s: %s", chat_id, msg_id, exc)
        finally:
            edited_messages.discard((chat_id, msg_id))

    async def schedule_auto_delete(chat_id: int, msg_id: int, *, fallback: int | None = None) -> None:
        delay_raw = await get_setting(chat_id, "autodelete_interval", "0")
        try:
            delay = int(delay_raw or 0)
        except (TypeError, ValueError):
            delay = 0
        if delay <= 0:
            if fallback is None:
                return
            delay = fallback
        asyncio.create_task(delete_later(chat_id, msg_id, delay))

    @app.on_message(filters.group & ~filters.service)
    async def moderate_message(client: Client, message: Message) -> None:
        if not message.from_user or message.from_user.is_bot:
            return
        if (await client.get_me()).id == message.from_user.id:
            return
        chat_id = message.chat.id
        user = message.from_user
        user_admin = bool(await is_admin(client, message, user.id))
        user_approved = bool(await is_approved(chat_id, user.id))
        if not user_admin and not user_approved:
            await schedule_auto_delete(chat_id, message.id)
        if not user_admin and not user_approved and await get_approval_mode(chat_id):
            await suppress_delete(message)
            await message.reply_text("❌ You are not approved to speak here.", quote=True)
            return
        if message.text or message.caption:
            text = message.text or message.caption or ""
            link_enabled = str(await get_setting(chat_id, "linkfilter", "0")) == "1"
            if link_enabled and contains_link(text) and not user_admin and not user_approved:
                await suppress_delete(message)
                count = await increment_warning(chat_id, user.id)
                reason = "You are not allowed to share links in this group."
                if count >= 3:
                    await client.restrict_chat_member(chat_id, user.id, ChatPermissions())
                    await reset_warning(chat_id, user.id)
                msg, kb = build_warning(count, user, reason, is_final=(count >= 3))
                await message.reply_text(msg, reply_markup=kb, parse_mode=ParseMode.HTML, quote=True)
                return
            bio_filter_enabled = await get_bio_filter(chat_id)
            if bio_filter_enabled and not user_admin and not user_approved:
                try:
                    user_info = await client.get_chat(user.id)
                    bio = getattr(user_info, "bio", "")
                except Exception:
                    bio = ""
                if bio and (len(bio) > MAX_BIO_LENGTH or contains_link(bio)):
                    await suppress_delete(message)
                    count = await increment_warning(chat_id, user.id)
                    reason = "Your bio contains a link or is too long, which is not allowed."
                    if count >= 3:
                        await client.restrict_chat_member(chat_id, user.id, ChatPermissions())
                        await reset_warning(chat_id, user.id)
                    msg, kb = build_warning(count, user, reason, is_final=(count >= 3))
                    await message.reply_text(msg, reply_markup=kb, parse_mode=ParseMode.HTML, quote=True)

    @app.on_edited_message(filters.group & ~filters.service)
    async def on_edit(client: Client, message: Message):
        if not message.from_user or message.from_user.is_bot:
            return
        user = message.from_user
        if bool(await is_admin(client, message, user.id)) or bool(
            await is_approved(message.chat.id, user.id)
        ):
            return
        if str(await get_setting(message.chat.id, "editmode", "0")) != "1":
            return
        key = (message.chat.id, message.id)
        if key not in edited_messages:
            edited_messages.add(key)
            await schedule_auto_delete(message.chat.id, message.id, fallback=0)

    @app.on_message(filters.new_chat_members)
    async def check_new_member_bio(client: Client, message: Message):
        chat_id = message.chat.id
        bio_filter_enabled = await get_bio_filter(chat_id)
        if not bio_filter_enabled:
            return
        for user in message.new_chat_members:
            if user.is_bot:
                continue
            if bool(await is_admin(client, message, user.id)) or bool(await is_approved(chat_id, user.id)):
                continue
            try:
                user_info = await client.get_chat(user.id)
                bio = getattr(user_info, "bio", "")
            except Exception:
                continue
            if bio and (len(bio) > MAX_BIO_LENGTH or contains_link(bio)):
                await suppress_delete(message)
                count = await increment_warning(chat_id, user.id)
                reason = "Your bio contains a link or is too long, which is not allowed."
                if count >= 3:
                    await client.restrict_chat_member(chat_id, user.id, ChatPermissions())
                    await reset_warning(chat_id, user.id)
                msg, kb = build_warning(count, user, reason, is_final=(count >= 3))
                await message.reply_text(msg, reply_markup=kb, parse_mode=ParseMode.HTML, quote=True)
