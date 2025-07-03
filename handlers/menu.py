"""Basic /start and /menu commands."""

import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import SUPPORT_CHAT_URL, DEVELOPER_URL
from utils.errors import catch_errors

logger = logging.getLogger(__name__)


async def _send_menu(client: Client, message: Message) -> None:
    user = message.from_user
    text = [
        "👋 Welcome! I'm alive and working.",
        "I'm a simple moderation bot.",
    ]
    if user:
        text.append(f"Your ID: <code>{user.id}</code>")
    me = await client.get_me()
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "➕ Add to Group",
                    url=f"https://t.me/{me.username}?startgroup=true",
                )
            ],
            [InlineKeyboardButton("ℹ️ Help", callback_data="help_tab")],
            [
                InlineKeyboardButton("👤 Developer", url=DEVELOPER_URL),
                InlineKeyboardButton("📣 Support", url=SUPPORT_CHAT_URL),
            ],
        ]
    )
    await message.reply_text("\n".join(text), reply_markup=buttons)


def register(app: Client) -> None:
    @app.on_message(filters.command("start") & filters.private)
    @catch_errors
    async def start_cmd(client: Client, message: Message):
        logger.info("/start from %s", message.from_user.id if message.from_user else None)
        await _send_menu(client, message)

    @app.on_message(filters.command("start") & ~filters.private)
    @catch_errors
    async def start_group_cmd(client: Client, message: Message):
        logger.info("/start in %s", message.chat.id)
        await message.reply_text("👋 Welcome! I'm alive and working. Please DM me to access the menu.")

    @app.on_message(filters.command("menu"))
    @catch_errors
    async def menu_cmd(client: Client, message: Message):
        logger.info("/menu in %s by %s", message.chat.id, message.from_user.id if message.from_user else None)
        if message.chat.type != "private":
            await message.reply_text("ℹ️ Please DM me for the menu.")
            return
        await _send_menu(client, message)
