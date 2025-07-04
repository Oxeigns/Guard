import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from utils.db import set_autodelete, get_autodelete
from utils.perms import is_admin
from utils.errors import catch_errors

logger = logging.getLogger(__name__)

DEFAULT_AUTODELETE_SECONDS = 60


def register(app: Client) -> None:
    def generate_markup() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🕐 5s", callback_data="autodel_5"),
                InlineKeyboardButton("⏱️ 30s", callback_data="autodel_30"),
                InlineKeyboardButton("🧹 Disable", callback_data="autodel_0"),
            ]
        ])

    def format_response(seconds: int) -> str:
        return (
            f"✅ <b>Auto-delete</b> is now set to <b>{seconds} seconds</b>."
            if seconds > 0
            else "🧹 <b>Auto-delete</b> has been <b>disabled</b>."
        )

    @app.on_message(filters.command(["setautodelete", "autodelete"]) & filters.group)
    @catch_errors
    async def set_autodel_command(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text("🔒 <b>Only admins can configure auto-delete.</b>", parse_mode=ParseMode.HTML)
            return

        if len(message.command) == 1:
            current = await get_autodelete(message.chat.id)
            await message.reply_text(
                f"<b>🕒 Current Auto-Delete Setting:</b> <code>{current}</code> seconds\n\n"
                "Select an option below or use:\n"
                "<code>/autodelete &lt;seconds&gt;</code>\n"
                "Use <code>0</code> to disable.",
                parse_mode=ParseMode.HTML,
                reply_markup=generate_markup()
            )
            return

        try:
            seconds = int(message.command[1])
            if seconds < 0:
                raise ValueError
        except ValueError:
            await message.reply_text(
                "⚠️ <b>Usage:</b> <code>/autodelete &lt;seconds&gt;</code>",
                parse_mode=ParseMode.HTML
            )
            return

        await set_autodelete(message.chat.id, seconds)
        await message.reply_text(format_response(seconds), parse_mode=ParseMode.HTML)

    @app.on_message(filters.command("autodeleteon") & filters.group)
    @catch_errors
    async def enable_autodelete(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text("🔒 <b>Only admins can enable auto-delete.</b>", parse_mode=ParseMode.HTML)
            return

        await set_autodelete(message.chat.id, DEFAULT_AUTODELETE_SECONDS)
        await message.reply_text(
            f"✅ <b>Auto-delete enabled</b>: <code>{DEFAULT_AUTODELETE_SECONDS}</code> seconds",
            parse_mode=ParseMode.HTML
        )

    @app.on_message(filters.command("autodeleteoff") & filters.group)
    @catch_errors
    async def disable_autodelete(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text("🔒 <b>Only admins can disable auto-delete.</b>", parse_mode=ParseMode.HTML)
            return

        await set_autodelete(message.chat.id, 0)
        await message.reply_text("🧹 <b>Auto-delete has been disabled.</b>", parse_mode=ParseMode.HTML)

    @app.on_callback_query(filters.regex(r"^autodel_(\d+)$"))
    @catch_errors
    async def handle_autodel_callback(client: Client, query: CallbackQuery):
        if not await is_admin(client, query.message, query.from_user.id):
            await query.answer("🚫 Only admins can do that.", show_alert=True)
            return

        seconds = int(query.data.split("_")[1])
        await set_autodelete(query.message.chat.id, seconds)
        await query.answer("✅ Updated")
        await query.message.edit_text(
            format_response(seconds),
            parse_mode=ParseMode.HTML
        )

    @app.on_message(filters.group & ~filters.service)
    @catch_errors
    async def enforce_autodelete(client: Client, message: Message):
        if not message.text and not message.caption:
            return
        if not message.from_user or message.from_user.is_bot:
            return
        if await is_admin(client, message, message.from_user.id):
            return

        delay = await get_autodelete(message.chat.id)
        if delay > 0:
            await asyncio.sleep(delay)
            try:
                await message.delete()
                logger.info("🧹 Auto-deleted message from %s in chat %s", message.from_user.id, message.chat.id)
            except Exception as e:
                logger.warning("Failed to auto-delete message from %s: %s", message.from_user.id, str(e))
