import os
import logging
from time import perf_counter
from pyrogram import Client
from pyrogram.enums import ParseMode, ChatType
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from utils.db import get_setting, toggle_setting, set_setting
from utils.perms import is_admin

logger = logging.getLogger(__name__)

BANNER_URL = os.getenv("BANNER_URL")
SUPPORT_CHAT_URL = os.getenv("SUPPORT_CHAT_URL", "https://t.me/botsyard")
DEVELOPER_URL = os.getenv("DEVELOPER_URL", "https://t.me/oxeign")
BOT_USERNAME = os.getenv("BOT_USERNAME", "OxeignBot")


async def build_group_panel(chat_id: int, client: Client) -> tuple[str, InlineKeyboardMarkup]:
    bio_status = await get_setting(chat_id, "biolink", "0") == "1"
    delete_enabled = await get_setting(chat_id, "autodelete", "0") == "1"
    delete_interval = await get_setting(chat_id, "autodelete_interval", "0")

    caption = (
        "<b>🛡️ Group Guard Panel</b>\n\n"
        f"🔗 Bio Filter: {'<b>✅ ON</b>' if bio_status else '<b>❌ OFF</b>'}\n"
        f"🗑️ Auto Delete: {'<b>✅ ' + delete_interval + 's</b>' if delete_enabled and delete_interval else '<b>❌ OFF</b>'}"
    )

    buttons = [
        [
            InlineKeyboardButton("✅ Approve", callback_data="cb_approve"),
            InlineKeyboardButton("🚫 Unapprove", callback_data="cb_unapprove"),
        ],
        [
            InlineKeyboardButton("🧹 Auto-Delete", callback_data="cb_toggle_autodel"),
            InlineKeyboardButton("🔗 Bio Filter", callback_data="cb_toggle_biolink"),
        ],
        [
            InlineKeyboardButton("📖 Help", callback_data="cb_help"),
            InlineKeyboardButton("📡 Ping", callback_data="cb_ping"),
        ],
        [
            InlineKeyboardButton("👨‍💻 Developer", url=DEVELOPER_URL),
            InlineKeyboardButton("💬 Support", url=SUPPORT_CHAT_URL),
        ],
    ]
    return caption, InlineKeyboardMarkup(buttons)


async def build_private_panel() -> tuple[str, InlineKeyboardMarkup]:
    caption = (
        "<b>🤖 Bot Control Panel</b>\n\n"
        "Use the buttons below to manage settings or get help."
    )
    buttons = [
        [
            InlineKeyboardButton("📖 Help", callback_data="cb_help"),
            InlineKeyboardButton("💬 Support", url=SUPPORT_CHAT_URL),
        ],
        [
            InlineKeyboardButton("👨‍💻 Developer", url=DEVELOPER_URL),
            InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true"),
        ],
    ]
    return caption, InlineKeyboardMarkup(buttons)


async def send_panel(client: Client, message: Message) -> None:
    if message.chat.type == ChatType.PRIVATE:
        caption, markup = await build_private_panel()
    else:
        caption, markup = await build_group_panel(message.chat.id, client)

    try:
        if BANNER_URL:
            await client.send_photo(
                chat_id=message.chat.id,
                photo=BANNER_URL,
                caption=caption,
                reply_markup=markup,
                parse_mode=ParseMode.HTML,
            )
        else:
            await message.reply_text(caption, reply_markup=markup, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.warning("Banner failed: %s", e)
        await message.reply_text(caption, reply_markup=markup, parse_mode=ParseMode.HTML)
