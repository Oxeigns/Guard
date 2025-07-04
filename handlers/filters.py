import asyncio
import logging
import re
from contextlib import suppress
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import (
    Message, ChatPermissions, InlineKeyboardButton,
    InlineKeyboardMarkup
)

from utils.errors import catch_errors
from utils.perms import is_admin
from utils.db import (
    get_setting,
    get_bio_filter,
    increment_warning,
    reset_warning,
    is_approved,
)

logger = logging.getLogger(__name__)

LINK_RE = re.compile(
    r"(?:https?://\S+|t\.me/\S+|tg://\S+|(?:\w+\.)+\w{2,})",
    re.IGNORECASE,
)
MAX_BIO_LENGTH = 800
SUPPORT_CHAT = "https://t.me/botsyard"


def contains_link(text: str) -> bool:
    return bool(LINK_RE.search(text or ""))


async def suppress_delete(message: Message):
    with suppress(Exception):
        await message.delete()


def build_warning(count: int, user, is_final: bool = False):
    name = f"@{user.username}" if user.username else f"{user.first_name} ({user.id})"
    support_btn = InlineKeyboardButton("📨 Support", url=SUPPORT_CHAT)

    if is_final:
        msg = (
            f"🔇 <b>Final Warning for {name}</b>\n\n"
            "Your bio contains a link or is too long.\n"
            "You have been <b>muted</b>.\n"
            "Fix your bio and contact support or an admin."
        )
        kb = InlineKeyboardMarkup([
            [support_btn],
            [InlineKeyboardButton("🔓 Unmute", callback_data=f"biofilter_unmute_{user.id}")]
        ])
    else:
        msg = (
            f"⚠️ <b>Warning {count}/3 for {name}</b>\n\n"
            "Your bio contains a link or is too long.\n"
            "Fix it before you're muted."
        )
        kb = InlineKeyboardMarkup([[support_btn]])

    return msg, kb


def register(app: Client) -> None:
    edited_messages: set[tuple[int, int]] = set()

    async def delete_later(chat_id: int, message_id: int, delay: int) -> None:
        await asyncio.sleep(max(delay, 0))
        try:
            await app.delete_messages(chat_id, message_id)
        except Exception as exc:
            logger.warning("Failed to delete %s/%s: %s", chat_id, message_id, exc)
        finally:
            edited_messages.discard((chat_id, message_id))

    async def schedule_auto_delete(chat_id: int, message_id: int, *, fallback: int = 900) -> None:
        delay = int(await get_setting(chat_id, "autodelete_interval", "0"))
        delay = delay if delay > 0 else fallback
        asyncio.create_task(delete_later(chat_id, message_id, delay))

    @app.on_message(filters.group & (filters.text | filters.caption))
    @catch_errors
    async def check_message_links(client: Client, message: Message):
        user = message.from_user
        chat_id = message.chat.id
        if not user or user.is_bot:
            return
        if await is_admin(client, message, user.id) or await is_approved(chat_id, user.id):
            return
        if await get_setting(chat_id, "linkfilter", "0") != "1":
            return
        if contains_link(message.text or message.caption or ""):
            await suppress_delete(message)
            count = await increment_warning(chat_id, user.id)
            if count >= 3:
                await client.restrict_chat_member(chat_id, user.id, ChatPermissions())
                await reset_warning(chat_id, user.id)
            msg, kb = build_warning(count, user, is_final=(count >= 3))
            await message.reply_text(msg, reply_markup=kb, parse_mode=ParseMode.HTML, quote=True)

    @app.on_message(filters.group & ~filters.service)
    @catch_errors
    async def enforce_autodelete(client: Client, message: Message):
        if not message.from_user or message.from_user.is_bot:
            return
        bot_id = (await client.get_me()).id
        if message.from_user.id != bot_id:
            await schedule_auto_delete(message.chat.id, message.id)

    @app.on_edited_message(filters.group & ~filters.service)
    @catch_errors
    async def on_edit(client: Client, message: Message):
        if not message.from_user or message.from_user.is_bot:
            return
        bot_id = (await client.get_me()).id
        if message.from_user.id != bot_id:
            key = (message.chat.id, message.id)
            if key not in edited_messages:
                edited_messages.add(key)
                await schedule_auto_delete(message.chat.id, message.id, fallback=900)

    @app.on_message(filters.new_chat_members)
    @catch_errors
    async def check_new_member_bio(client: Client, message: Message):
        chat_id = message.chat.id
        if not await get_bio_filter(chat_id):
            return

        for user in message.new_chat_members:
            if user.is_bot or await is_admin(client, message, user.id) or await is_approved(chat_id, user.id):
                continue
            try:
                user_info = await client.get_chat(user.id)
                bio = getattr(user_info, "bio", "")
            except Exception:
                continue
            if not bio or (len(bio) <= MAX_BIO_LENGTH and not contains_link(bio)):
                continue

            await suppress_delete(message)
            count = await increment_warning(chat_id, user.id)
            if count >= 3:
                await client.restrict_chat_member(chat_id, user.id, ChatPermissions())
                await reset_warning(chat_id, user.id)
            msg, kb = build_warning(count, user, is_final=(count >= 3))
            await message.reply_text(msg, reply_markup=kb, parse_mode=ParseMode.HTML, quote=True)
