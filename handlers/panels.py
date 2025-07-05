import os
from html import escape
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from utils.perms import is_admin
from utils.db import get_setting, get_bio_filter
from config import OWNER_ID

# Default image for all welcome messages
PANEL_IMAGE_URL = os.getenv("PANEL_IMAGE_URL", "https://files.catbox.moe/uvqeln.jpg")


def mention_html(user_id: int, name: str) -> str:
    return f'<a href="tg://user?id={user_id}">{escape(name)}</a>'


# Build the main inline keyboard
async def build_start_panel(is_admin: bool = False, *, is_owner: bool = False, include_back: bool = False) -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton("📘 Commands", callback_data="cb_help_start")]]
    if is_admin:
        buttons.insert(0, [InlineKeyboardButton("⚙️ Settings", callback_data="open_settings")])
    if is_owner:
        buttons.append([InlineKeyboardButton("📢 Broadcast", callback_data="help_broadcast")])
    if include_back:
        buttons.append([InlineKeyboardButton("🔙 Back", callback_data="cb_back_panel")])
    return InlineKeyboardMarkup(buttons)


# Send welcome/start panel (used for /start, /help, /menu)
async def send_start(client, message: Message, *, include_back: bool = False) -> None:
    """Send the main panel in private chats or the settings panel in groups."""
    bot_user = await client.get_me()
    user = message.from_user
    chat = message.chat
    is_owner = user.id == OWNER_ID

    if chat.type in {"group", "supergroup"}:  # group context
        if not await is_admin(client, message):
            await message.reply_text("🔒 Only admins can view the control panel.")
            return
        markup = await build_settings_panel(chat.id)
        caption = "⚙️ <b>Group Settings</b>"
    else:  # private chat
        markup = await build_start_panel(
            bool(await is_admin(client, message)),
            is_owner=is_owner,
            include_back=include_back,
        )
        caption = (
            f"🎉 <b>Welcome to {bot_user.first_name}</b>\n\n"
            f"Hello {mention_html(user.id, user.first_name)}!\n\n"
            "I'm here to help manage your group efficiently.\n"
            "You can tap the buttons below to explore available features.\n\n"
            "✅ Works in groups\n🛠 Admin-only settings\n🧠 Smart automation tools"
        )

    await message.reply_photo(
        photo=PANEL_IMAGE_URL,
        caption=caption,
        reply_markup=markup,
        parse_mode=ParseMode.HTML,
    )


# Alias for group usage - now uses same layout as send_start
async def send_control_panel(client, message: Message) -> None:
    await send_start(client, message)
    

# Help menu inline keyboard
def get_help_keyboard(back_cb: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛡️ BioMode", callback_data="help_biomode")],
        [InlineKeyboardButton("🧹 AutoDelete", callback_data="help_autodelete")],
        [InlineKeyboardButton("🔗 LinkFilter", callback_data="help_linkfilter")],
        [InlineKeyboardButton("✏️ EditMode", callback_data="help_editmode")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="help_broadcast")],
        [
            InlineKeyboardButton("👨‍💻 Developer", callback_data="help_developer"),
            InlineKeyboardButton("🆘 Support", callback_data="help_support")
        ],
        [InlineKeyboardButton("🔙 Back", callback_data=back_cb)]
    ])


# Settings panel keyboard
async def build_settings_panel(chat_id: int) -> InlineKeyboardMarkup:
    bio = await get_bio_filter(chat_id)
    link = str(await get_setting(chat_id, "linkfilter", "0")) == "1"
    edit = str(await get_setting(chat_id, "editmode", "0")) == "1"
    delay = int(await get_setting(chat_id, "autodelete_interval", "0") or 0)
    buttons = [
        [InlineKeyboardButton(f"🌐 BioLink {'✅' if bio else '❌'}", callback_data="toggle_biolink")],
        [InlineKeyboardButton(f"🔗 LinkFilter {'✅' if link else '❌'}", callback_data="toggle_linkfilter")],
        [InlineKeyboardButton(f"✏️ EditFilter {'✅' if edit else '❌'}", callback_data="toggle_editfilter")],
        [InlineKeyboardButton(f"🧹 AutoDelete {delay}s" if delay else "🧹 AutoDelete Off", callback_data="toggle_autodelete")],
        [InlineKeyboardButton("🔙 Back", callback_data="cb_start")],
    ]
    return InlineKeyboardMarkup(buttons)
