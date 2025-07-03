"""Settings panel with inline buttons."""

from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from config import BANNER_URL
from utils.perms import is_admin

# Updated button grid (as per user request: removed Anti-Spam, Alphabets, Porn, Night)
SETTINGS_PANEL = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("📜 Regulation", callback_data="regulation"),
        InlineKeyboardButton("💬 Welcome", callback_data="welcome"),
    ],
    [
        InlineKeyboardButton("👋 Goodbye ᴺᴱᵂ", callback_data="goodbye"),
        InlineKeyboardButton("🚫 Anti-Flood", callback_data="antiflood"),
    ],
    [
        InlineKeyboardButton("🧠 Captcha", callback_data="captcha"),
        InlineKeyboardButton("🔦 Checks ᴺᴱᵂ", callback_data="checks"),
    ],
    [
        InlineKeyboardButton("📣 @Admin", callback_data="admin"),
        InlineKeyboardButton("🔐 Blocks", callback_data="blocks"),
    ],
    [
        InlineKeyboardButton("📷 Media", callback_data="media"),
        InlineKeyboardButton("❗ Warns", callback_data="warns"),
    ],
    [
        InlineKeyboardButton("🔔 Tag", callback_data="tag"),
        InlineKeyboardButton("🔗 Link", callback_data="link"),
    ],
    [
        InlineKeyboardButton("📬 Approval mode", callback_data="approval"),
        InlineKeyboardButton("🗑 Deleting Messages", callback_data="delmsg"),
    ],
    [
        InlineKeyboardButton("🇬🇧 Lang", callback_data="lang"),
        InlineKeyboardButton("✅ Close", callback_data="close"),
        InlineKeyboardButton("📦 Other", callback_data="other"),
    ],
])


def register(app: Client):
    @app.on_message(filters.command(["start", "help", "menu"]))
    async def open_panel(client: Client, message: Message):
        if message.chat.type == "private" or await is_admin(client, message):
            await message.reply_photo(
                photo=BANNER_URL,
                caption=(
                    "🔧 **SETTINGS PANEL**\n"
                    "Select one of the settings that you want to change.\n\n"
                    "Group: `BOTS ✺ YARD DISCUSSION`"
                ),
                reply_markup=SETTINGS_PANEL,
                parse_mode="Markdown",
            )

    @app.on_callback_query()
    async def handle_clicks(client: Client, query: CallbackQuery):
        if query.data == "close":
            await query.message.delete()
            return

        await query.answer()
        await query.message.edit_text(
            f"🛠 *You selected:* `{query.data}`\nThat setting's options will be shown soon.",
            parse_mode="Markdown",
        )
