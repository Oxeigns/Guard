"""Inline control panel."""

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message


PANEL = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("🛡 Bio Filter Settings", callback_data="bio")],
        [InlineKeyboardButton("🕒 AutoDelete Settings", callback_data="auto")],
        [InlineKeyboardButton("✅ Approve", callback_data="approve"),
         InlineKeyboardButton("❌ Unapprove", callback_data="unapprove")],
        [InlineKeyboardButton("📋 View Approved", callback_data="list")],
        [InlineKeyboardButton("📣 Support Channel", url="https://t.me/botsyard")],
        [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/oxeigm")],
        [InlineKeyboardButton("❎ Close Panel", callback_data="close")],
    ]
)


@Client.on_message(filters.command(["panel", "start", "help", "menu"]) & filters.group)
async def open_panel(client: Client, message: Message) -> None:
    """Send the inline control panel."""
    await message.reply(
        "*Control Panel*",
        reply_markup=PANEL,
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )
