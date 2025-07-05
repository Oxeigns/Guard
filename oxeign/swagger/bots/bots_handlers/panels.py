import os
from html import escape
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import SUPPORT_CHAT_URL, DEVELOPER_URL
from utils.perms import is_admin
from utils.db import get_setting, get_bio_filter

PANEL_IMAGE_URL = os.getenv("PANEL_IMAGE_URL", "https://files.catbox.moe/uvqeln.jpg")


def mention_html(user_id: int, name: str) -> str:
    return f'<a href="tg://user?id={user_id}">{escape(name)}</a>'


async def build_start_panel(is_admin: bool = False, *, include_back: bool = False) -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton("📘 Commands", callback_data="cb_help_start")]]
    if is_admin:
        buttons.insert(0, [InlineKeyboardButton("⚙️ Settings", callback_data="cb_start")])
    if include_back:
        buttons.append([InlineKeyboardButton("🔙 Back", callback_data="cb_back_panel")])
    return InlineKeyboardMarkup(buttons)


async def send_start(client, message: Message, *, include_back: bool = False) -> None:
    bot_user = await client.get_me()
    user = message.from_user
    markup = await build_start_panel(await is_admin(client, message), include_back=include_back)

    await message.reply_photo(
        photo=PANEL_IMAGE_URL,
        caption=(
            f"🎉 <b>Welcome to {bot_user.first_name}</b>\n\n"
            f"Hello {mention_html(user.id, user.first_name)}!\n\n"
            "I'm here to help manage your group efficiently.\n"
            "You can tap the buttons below to explore available features.\n\n"
            "✅ Works in groups\n🛠 Admin-only settings\n🧠 Smart automation tools"
        ),
        reply_markup=markup,
        parse_mode=ParseMode.HTML,
    )


def get_help_keyboard(back_cb: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛡️ BioMode", callback_data="help_biomode")],
        [InlineKeyboardButton("🧹 AutoDelete", callback_data="help_autodelete")],
        [InlineKeyboardButton("🔗 LinkFilter", callback_data="help_linkfilter")],
        [InlineKeyboardButton("✏️ EditMode", callback_data="help_editmode")],
        [
            InlineKeyboardButton("👨‍💻 Developer", callback_data="help_developer"),
            InlineKeyboardButton("🆘 Support", callback_data="help_support")
        ],
        [InlineKeyboardButton("🔙 Back", callback_data=back_cb)]
    ])


async def build_group_panel(chat_id: int, client) -> tuple[str, InlineKeyboardMarkup]:
    interval = int(await get_setting(chat_id, "autodelete_interval", "0"))
    biolink = await get_bio_filter(chat_id)
    linkfilter = await get_setting(chat_id, "linkfilter", "0") == "1"
    editmode = await get_setting(chat_id, "editmode", "0") == "1"

    ad_status = f"{interval}s" if interval > 0 else "OFF"

    caption = (
        "<b>Group Control Panel</b>\n"
        f"🧹 Auto-Delete: <b>{ad_status}</b>\n"
        f"🛡 BioFilter: <b>{'ON ✅' if biolink else 'OFF ❌'}</b>\n"
        f"🔗 LinkFilter: <b>{'ON ✅' if linkfilter else 'OFF ❌'}</b>\n"
        f"✏️ EditMode: <b>{'ON ✅' if editmode else 'OFF ❌'}</b>"
    )

    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="cb_start")],
        [InlineKeyboardButton("📘 Commands", callback_data="cb_help_panel")]
    ])

    return caption, markup


async def send_control_panel(client, message: Message) -> None:
    caption, markup = await build_group_panel(message.chat.id, client)
    await message.reply_text(caption, reply_markup=markup, parse_mode=ParseMode.HTML)
