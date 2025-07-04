"""Bio link detection and progressive moderation."""

import logging
import re
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import (
    Message,
    ChatPermissions,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

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


def build_warning_message(
    count: int, restricted: bool = False
) -> tuple[str, InlineKeyboardMarkup | None]:
    if restricted:
        msg = (
            "🔞 *Final Warning:* You have been restricted due to repeated"
            " violations."
        )
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🖘 Appeal Restriction",
                        url="https://t.me/your_support_bot",
                    )
                ]
            ]
        )
    elif count == 2:
        msg = (
            "\u26a0\ufe0f *Warning 2:* Last chance! Please remove links or long bio"
            " content."
        )
        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton("\u2753 What\u2019s Wrong?", callback_data="why_bio_block")]]
        )
    elif count == 1:
        msg = (
            "\u26a0\ufe0f *Warning 1:* Bio with links or excessive length is not"
            " allowed."
        )
        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton("\u2139\ufe0f Learn More", callback_data="why_bio_block")]]
        )
    else:
        msg = "\u26a0\ufe0f Warning issued."
        buttons = None
    return msg, buttons


def register(app: Client) -> None:

    @app.on_message(filters.group & filters.text)
    @catch_errors
    async def bio_filter(client: Client, message: Message):
        chat_id = message.chat.id
        user = message.from_user

        if not user or user.is_bot:
            return
        if not await get_bio_filter(chat_id):
            return
        if await is_admin(client, message, user.id) or await is_approved(chat_id, user.id):
            return

        try:
            user_full = await client.get_chat(user.id)
            bio = getattr(user_full, "bio", "")
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to fetch bio for user %s: %s", user.id, exc)
            return

        if not bio or (len(bio) <= MAX_BIO_LENGTH and not contains_link(bio)):
            return

        try:
            await message.delete()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to delete message in chat %s: %s", chat_id, exc)

        count = await increment_warning(chat_id, user.id)
        restricted = False

        if count >= 3:
            await client.restrict_chat_member(chat_id, user.id, ChatPermissions())
            await reset_warning(chat_id, user.id)
            restricted = True

        msg, buttons = build_warning_message(count, restricted)
        await message.reply_text(
            msg,
            reply_markup=buttons,
            quote=True,
            parse_mode=ParseMode.MARKDOWN,
        )

    @app.on_message(filters.new_chat_members)
    @catch_errors
    async def new_member_check(client: Client, message: Message):
        chat_id = message.chat.id

        if not await get_bio_filter(chat_id):
            return

        for user in message.new_chat_members:
            if user.is_bot:
                continue
            if await is_admin(client, message, user.id) or await is_approved(chat_id, user.id):
                continue

            try:
                user_full = await client.get_chat(user.id)
                bio = getattr(user_full, "bio", "")
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to get bio for user %s: %s", user.id, exc)
                continue

            if not bio or (len(bio) <= MAX_BIO_LENGTH and not contains_link(bio)):
                continue

            try:
                await message.delete()
            except Exception as exc:  # noqa: BLE001
                logger.warning("Cannot delete new member message: %s", exc)
                await message.reply_text(
                    "\u274c I can't delete system messages. Please ensure I have 'Delete Messages' rights.",
                    quote=True,
                    parse_mode=ParseMode.MARKDOWN,
                )

            count = await increment_warning(chat_id, user.id)
            restricted = False

            if count >= 3:
                await client.restrict_chat_member(chat_id, user.id, ChatPermissions())
                await reset_warning(chat_id, user.id)
                restricted = True

            msg, buttons = build_warning_message(count, restricted)
            await message.reply_text(
                msg,
                reply_markup=buttons,
                quote=True,
                parse_mode=ParseMode.MARKDOWN,
            )

    @app.on_callback_query(filters.regex("why_bio_block"))
    async def explain_bio_block(client: Client, callback_query):
        await callback_query.answer()
        await callback_query.message.reply_text(
            "Your profile bio may contain links or be too long. This is restricted to protect the group from spam/scams. "
            "Please edit your bio to avoid moderation.",
            parse_mode=ParseMode.MARKDOWN,
        )

