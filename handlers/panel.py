"""Inline control panel."""

from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    CallbackQuery,
)

from utils.storage import Storage

storage = Storage()


PANEL = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("🛡 Bio Filter Settings", callback_data="bio")],
        [InlineKeyboardButton("🕒 AutoDelete Settings", callback_data="auto")],
        [InlineKeyboardButton("✅ Approve", callback_data="approve"),
         InlineKeyboardButton("❌ Unapprove", callback_data="unapprove")],
        [InlineKeyboardButton("📋 View Approved", callback_data="list")],
        [InlineKeyboardButton("📣 Support Channel", url="https://t.me/botsyard")],
        [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/oxeign")],
        [InlineKeyboardButton("❎ Close Panel", callback_data="close")],
    ]
)


@Client.on_message(filters.command(["panel", "start", "help", "menu"]) & filters.group)
async def open_panel(client: Client, message: Message) -> None:
    """Send the inline control panel."""
    await message.reply(
        "*Control Panel*",
        reply_markup=PANEL,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )

@Client.on_callback_query(filters.regex("^close$"))
async def close_panel(_, query: CallbackQuery) -> None:
    """Close the inline panel."""
    await query.message.delete()


@Client.on_callback_query(filters.regex("^list$"))
async def show_approved(client: Client, query: CallbackQuery) -> None:
    """Display approved users via callback."""
    users = await storage.get_approved_users(query.message.chat.id)
    if not users:
        text = "No approved users."
    else:
        mentions = []
        for uid in users:
            user = await client.get_users(uid)
            mentions.append(user.mention)
        text = "*Approved users:*\n" + "\n".join(mentions)
    await query.message.edit_text(text, parse_mode=ParseMode.MARKDOWN)

