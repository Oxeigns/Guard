"""Auto-delete messages after a delay in group chats only."""

import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from utils.db import set_autodelete, get_autodelete
from utils.perms import is_admin
from utils.errors import catch_errors

logger = logging.getLogger(__name__)


def register(app: Client) -> None:
    @app.on_message(filters.command(["setautodelete", "autodelete"]))
    @catch_errors
    async def set_autodel(client: Client, message: Message):
        if message.chat.type not in {"group", "supergroup"}:
            return

        user_id = message.from_user.id if message.from_user else None
        logger.info(
            "%s command in %s by %s",
            message.command[0],
            message.chat.id,
            user_id,
        )

        if not await is_admin(client, message):
            await message.reply_text("❌ You must be an admin to use this command.")
            return

        if len(message.command) == 1:
            current = await get_autodelete(message.chat.id)
            text = (
                f"🕒 **Current Auto-Delete Setting:** `{current}` seconds\n\n"
                "To change it, use:\n"
                "`/autodelete <seconds>`\n"
                "Use `0` to disable."
            )
            await message.reply_text(
                text,
                parse_mode="markdown",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Disable", callback_data="autodel_0")]]
                ),
            )
            return

        try:
            seconds = int(message.command[1])
            if seconds < 0:
                raise ValueError
        except (IndexError, ValueError):
            await message.reply_text(
                "⚠️ Usage: `/autodelete <seconds>`", parse_mode="markdown"
            )
            return

        await set_autodelete(message.chat.id, seconds)

        msg = (
            f"✅ Auto-delete enabled: **{seconds} seconds**."
            if seconds > 0
            else "🧹 Auto-delete has been **disabled**."
        )
        await message.reply_text(msg, parse_mode="markdown")

    @app.on_callback_query(filters.regex(r"^autodel_(\d+)$"))
    @catch_errors
    async def autodel_cb(client: Client, query: CallbackQuery):
        if not await is_admin(client, query.message, query.from_user.id):
            await query.answer("Admins only!", show_alert=True)
            return

        seconds = int(query.data.split("_", 1)[1])
        await set_autodelete(query.message.chat.id, seconds)
        msg = (
            f"✅ Auto-delete enabled: **{seconds} seconds**."
            if seconds > 0
            else "🧹 Auto-delete has been **disabled**."
        )
        await query.answer("Updated")
        await query.message.edit_text(msg, parse_mode="markdown")

    @app.on_message(filters.group & ~filters.service)
    @catch_errors
    async def autodelete_handler(client: Client, message: Message):
        if message.chat.type not in {"group", "supergroup"}:
            return

        if not (message.text or message.caption):
            return

        if message.from_user is None or message.from_user.is_bot:
            return

        if await is_admin(client, message, message.from_user.id):
            return

        delay = await get_autodelete(message.chat.id)
        if delay > 0:
            await asyncio.sleep(delay)
            try:
                await message.delete()
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Failed to delete message in %s: %s", message.chat.id, exc
                )

