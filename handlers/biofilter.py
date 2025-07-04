"""Bio link moderation with 3 warnings, mute, and admin unmute button."""

import logging
import re
import config
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

LINK_RE = re.compile(r"https?://\S+|t\.me/\S+|\w+\.\w{2,}", re.IGNORECASE)
MAX_BIO_LENGTH = 800
SUPPORT_CHAT_URL = getattr(config, "SUPPORT_CHAT_URL", "https://t.me/botsyard")


def contains_link(text: str) -> bool:
    return bool(LINK_RE.search(text or ""))


def build_warning(count: int, user, is_final=False) -> tuple[str, InlineKeyboardMarkup]:
    name = f"@{user.username}" if user.username else f"{user.first_name} ({user.id})"
    support_btn = InlineKeyboardButton("📨 Contact Support", url=SUPPORT_CHAT_URL)

    if is_final:
        msg = (
            f"🔇 <b>Final Warning for {name}</b>\n\n"
            "Your bio contains links or is too long.\n"
            "You have been <b>muted</b> in this group.\n"
            "Please fix your bio to regain access."
        )
        buttons = [
            [support_btn],
            [InlineKeyboardButton("🔓 Unmute", callback_data=f"unmute_user_{user.id}")]
        ]
    else:
        msg = (
            f"⚠️ <b>Warning {count}/3 for {name}</b>\n\n"
            "Your bio contains links or is too long.\n"
            "Please fix it to avoid being muted."
        )
        buttons = [[support_btn]]

    return msg, InlineKeyboardMarkup(buttons)


def register(app: Client) -> None:

    async def handle_bio_violation(client: Client, message: Message, user):
        try:
            await message.delete()
        except Exception as e:
            logger.warning("Couldn't delete message: %s", e)

        chat_id = message.chat.id
        user_id = user.id

        count = await increment_warning(chat_id, user_id)
        logger.info("User %s warning %d in chat %s", user_id, count, chat_id)

        if count >= 3:
            # Mute: Remove all permissions
            await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
            await reset_warning(chat_id, user_id)
            msg, kb = build_warning(count, user, is_final=True)
        else:
            msg, kb = build_warning(count, user, is_final=False)

        await message.reply_text(
            msg,
            reply_markup=kb,
            parse_mode=ParseMode.HTML,
            quote=True
        )

    @app.on_message(filters.group & filters.text)
    @catch_errors
    async def check_message_bio(client: Client, message: Message):
        user = message.from_user
        chat_id = message.chat.id

        if not user or user.is_bot:
            return
        if not await get_bio_filter(chat_id):
            return
        if await is_admin(client, message, user.id) or await is_approved(chat_id, user.id):
            return

        try:
            user_data = await client.get_chat(user.id)
            bio = getattr(user_data, "bio", "")
        except Exception as e:
            logger.warning("Bio fetch failed: %s", e)
            return

        if len(bio) > MAX_BIO_LENGTH or contains_link(bio):
            await handle_bio_violation(client, message, user)

    @app.on_message(filters.new_chat_members)
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

            try:
                user_data = await client.get_chat(user.id)
                bio = getattr(user_data, "bio", "")
            except Exception as e:
                logger.warning("Couldn't get bio for new member: %s", e)
                continue

            if len(bio) > MAX_BIO_LENGTH or contains_link(bio):
                try:
                    await message.delete()
                except Exception:
                    pass
                await handle_bio_violation(client, message, user)

    @app.on_callback_query(filters.regex(r"^unmute_user_(\d+)$"))
    @catch_errors
    async def unmute_user_cb(client: Client, query: CallbackQuery):
        user_id = int(query.matches[0].group(1))
        chat_id = query.message.chat.id

        if not await is_admin(client, query.message, query.from_user.id):
            await query.answer("Only admins can unmute.", show_alert=True)
            return

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
            await query.message.reply_text("🔓 User has been unmuted by admin.", quote=True)
        except Exception as e:
            logger.error("Unmute failed: %s", e)
            await query.answer("❌ Failed to unmute.")
