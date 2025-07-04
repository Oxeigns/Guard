"""Bio link moderation with 3 warnings, mute, and admin unmute button."""

import logging
import re
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import (
    Message,
    CallbackQuery,
    ChatPermissions,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from utils.db import (
    get_bio_filter,
    is_approved,
    increment_warning,
    reset_warning,
)
from utils.errors import catch_errors
from utils.perms import is_admin

logger = logging.getLogger(__name__)

LINK_RE = re.compile(r"(https?://\S+|t\.me/\S+|tg://\S+|@[\w\d_]+|\w+\.\w{2,})", re.IGNORECASE)
MAX_BIO_LENGTH = 800
SUPPORT_CHAT = "https://t.me/botsyard"  # Load from config ideally


def contains_link(text: str) -> bool:
    return bool(LINK_RE.search(text or ""))


def build_warning(count: int, user, is_final=False) -> tuple[str, InlineKeyboardMarkup]:
    name = f"@{user.username}" if user.username else f"{user.first_name} ({user.id})"
    support_btn = InlineKeyboardButton("📨 Support", url=SUPPORT_CHAT)

    if is_final:
        msg = (
            f"🔇 <b>Final Warning for {name}</b>\n\n"
            "Your bio contains links or is too long.\n"
            "You have been <b>muted</b> in this group.\n"
            "Fix your bio and ask admin to unmute you."
        )
        kb = InlineKeyboardMarkup([
            [support_btn],
            [InlineKeyboardButton("🔓 Unmute", callback_data=f"unmute_user_{user.id}")]
        ])
    else:
        msg = (
            f"⚠️ <b>Warning {count}/3 for {name}</b>\n\n"
            "Your bio contains links or is too long.\n"
            "Fix it to avoid being muted."
        )
        kb = InlineKeyboardMarkup([[support_btn]])

    return msg, kb


def register(app: Client) -> None:

    async def process_user(client: Client, message: Message, user):
        chat_id = message.chat.id
        user_id = user.id

        try:
            user_data = await client.get_chat(user_id)
            bio = getattr(user_data, "bio", "")
        except Exception as e:
            logger.warning("Couldn't fetch bio for %s: %s", user_id, e)
            return

        if not bio or (len(bio) <= MAX_BIO_LENGTH and not contains_link(bio)):
            return

        # Delete user's message
        try:
            await message.delete()
            logger.debug("Deleted message from user %s due to bad bio", user_id)
        except Exception as e:
            logger.warning("Failed to delete message from %s: %s", user_id, e)

        count = await increment_warning(chat_id, user_id)
        logger.info("Bio warning %d for %s in chat %s", count, user_id, chat_id)

        if count >= 3:
            await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
            await reset_warning(chat_id, user_id)
            msg, kb = build_warning(count, user, is_final=True)
        else:
            msg, kb = build_warning(count, user, is_final=False)

        await message.reply_text(msg, reply_markup=kb, parse_mode=ParseMode.HTML, quote=True)

    @app.on_message(filters.group & filters.text)
    @catch_errors
    async def on_message_check_bio(client: Client, message: Message):
        user = message.from_user
        chat_id = message.chat.id

        if not user or user.is_bot:
            return
        if not await get_bio_filter(chat_id):
            return
        if await is_admin(client, message, user.id) or await is_approved(chat_id, user.id):
            return

        await process_user(client, message, user)

    @app.on_message(filters.new_chat_members)
    @catch_errors
    async def on_new_user_check_bio(client: Client, message: Message):
        chat_id = message.chat.id
        if not await get_bio_filter(chat_id):
            return

        for user in message.new_chat_members:
            if user.is_bot:
                continue
            if await is_admin(client, message, user.id) or await is_approved(chat_id, user.id):
                continue
            await process_user(client, message, user)

    @app.on_callback_query(filters.regex(r"^unmute_user_(\d+)$"))
    @catch_errors
    async def unmute_user_cb(client: Client, query: CallbackQuery):
        import re
        match = re.match(r"^unmute_user_(\d+)$", query.data)
        if not match:
            return await query.answer("Invalid callback.")

        user_id = int(match.group(1))
        chat_id = query.message.chat.id

        if not await is_admin(client, query.message, query.from_user.id):
            return await query.answer("Only admins can unmute.", show_alert=True)

        try:
            await client.restrict_chat_member(chat_id, user_id, ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=False,
                can_invite_users=True,
                can_pin_messages=False
            ))
            await query.answer("✅ User unmuted.")
            await query.message.reply_text(
                f"🔓 User <a href='tg://user?id={user_id}'>unmuted</a>.",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error("Unmute failed: %s", e)
            await query.answer("❌ Failed to unmute.")
