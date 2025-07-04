import os
import logging
from contextlib import suppress
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatType
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from utils.db import get_setting
from utils.perms import is_admin

HELP_IMAGE_URL = os.getenv("PANEL_IMAGE_URL", "https://files.catbox.moe/uvqeln.jpg")

def register_help_ui(app: Client) -> None:

    @app.on_message(filters.command("help") & filters.group)
    async def show_help_panel(client: Client, message: Message):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛡️ BioMode", callback_data="help_biomode")],
            [InlineKeyboardButton("📝 Long Message", callback_data="help_long")],
            [InlineKeyboardButton("🔗 LinkFilter", callback_data="help_linkfilter")],
            [InlineKeyboardButton("🔙 Back", callback_data="help_back")],
        ])

        await client.send_photo(
            chat_id=message.chat.id,
            photo=HELP_IMAGE_URL,
            caption=(
                "📚 <b>Bot Command Help</b>\n\n"
                "Here you'll find details for all available plugins and features.\n\n"
                "👇 Tap the buttons below to view help for each module:"
            ),
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )

    @app.on_callback_query()
    async def help_callback_handler(client: Client, cb):
        help_data = {
            "help_biomode": (
                "🛡️ <b>BioMode</b>\n\n"
                "<i>Blocks users with URLs in their bio from sending messages.</i>\n\n"
                "<b>Commands:</b>\n"
                "• <code>/biolink on</code>\n"
                "• <code>/biolink off</code>\n\n"
                "👮 Admin-only setting."
            ),
            "help_long": (
                "📝 <b>Long Message Filter</b>\n\n"
                "<i>Auto-deletes messages longer than a set limit.</i>\n\n"
                "<b>Usage:</b>\n"
                "• <code>/setlonglimit 800</code> (Range: 200–4000)\n"
                "Default: 800 characters"
            ),
            "help_linkfilter": (
                "🔗 <b>Link Filter</b>\n\n"
                "<i>Removes any links sent by non-admins in the group.</i>\n\n"
                "<b>Commands:</b>\n"
                "• <code>/linkfilter on</code>\n"
                "• <code>/linkfilter off</code>\n"
                "👮 Admin-only setting."
            ),
        }

        if cb.data in help_data:
            await cb.message.edit_caption(
                caption=help_data[cb.data],
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="help_back")]
                ]),
                parse_mode=ParseMode.HTML
            )

        elif cb.data == "help_back":
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🛡️ BioMode", callback_data="help_biomode")],
                [InlineKeyboardButton("📝 Long Message", callback_data="help_long")],
                [InlineKeyboardButton("🔗 LinkFilter", callback_data="help_linkfilter")],
                [InlineKeyboardButton("🔙 Back", callback_data="help_back")],
            ])
            await cb.message.edit_caption(
                caption=(
                    "📚 <b>Bot Command Help</b>\n\n"
                    "Here you'll find details for all available plugins and features.\n\n"
                    "👇 Tap the buttons below to view help for each module:"
                ),
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )

        await cb.answer()


# --- Legacy control panel helpers used by other modules ---

logger = logging.getLogger(__name__)
PANEL_IMAGE_URL = os.getenv("PANEL_IMAGE_URL")
SUPPORT_CHAT_URL = os.getenv("SUPPORT_CHAT_URL", "https://t.me/botsyard")
DEVELOPER_URL = os.getenv("DEVELOPER_URL", "https://t.me/oxeign")
BOT_USERNAME = os.getenv("BOT_USERNAME", "OxeignBot")


async def build_start_panel(is_admin_user: bool) -> InlineKeyboardMarkup:
    """Return inline buttons for the /start panel."""
    buttons = [
        [
            InlineKeyboardButton(
                "➕ Add Me to Group",
                url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
            ),
            InlineKeyboardButton("📚 Help & Commands", callback_data="cb_help_start"),
        ],
        [
            InlineKeyboardButton("🛟 Support", url=SUPPORT_CHAT_URL),
            InlineKeyboardButton("👨\u200d💻 Developer", url=DEVELOPER_URL),
        ],
    ]
    if is_admin_user:
        buttons.append([InlineKeyboardButton("🧰 Control Panel", callback_data="cb_open_panel")])
    return InlineKeyboardMarkup(buttons)


async def build_group_panel(chat_id: int, client: Client) -> tuple[str, InlineKeyboardMarkup]:
    """Return caption and buttons for the group control panel."""
    bio_status = await get_setting(chat_id, "biolink", "0") == "1"
    link_status = await get_setting(chat_id, "linkfilter", "0") == "1"
    delete_enabled = await get_setting(chat_id, "autodelete", "0") == "1"
    edit_status = await get_setting(chat_id, "editmode", "0") == "1"
    delete_interval = await get_setting(chat_id, "autodelete_interval", "0")

    caption = (
        "<b>🛡️ Group Guard Panel</b>\n\n"
        f"🔗 Bio Filter: {'<b>✅ ON</b>' if bio_status else '<b>❌ OFF</b>'}\n"
        f"🌐 Link Filter: {'<b>✅ ON</b>' if link_status else '<b>❌ OFF</b>'}\n"
        f"🗑️ Auto Delete: {'<b>✅ ' + delete_interval + 's</b>' if delete_enabled and delete_interval else '<b>❌ OFF</b>'}\n"
        f"📝 Edit Delete: {'<b>✅ 15m</b>' if edit_status else '<b>❌ OFF</b>'}"
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
            InlineKeyboardButton("🔗 Link Filter", callback_data="cb_toggle_linkfilter"),
            InlineKeyboardButton("📝 Edit Delete", callback_data="cb_toggle_editmode"),
        ],
        [
            InlineKeyboardButton("📖 Help", callback_data="cb_help_panel"),
            InlineKeyboardButton("📡 Ping", callback_data="cb_ping"),
        ],
        [
            InlineKeyboardButton("👨‍💻 Developer", url=DEVELOPER_URL),
            InlineKeyboardButton("💬 Support", url=SUPPORT_CHAT_URL),
        ],
    ]
    return caption, InlineKeyboardMarkup(buttons)


async def build_private_panel() -> tuple[str, InlineKeyboardMarkup]:
    """Return caption and buttons for the private control panel."""
    caption = (
        "<b>🤖 Bot Control Panel</b>\n\n"
        "Use the buttons below to manage settings or get help."
    )
    buttons = [
        [
            InlineKeyboardButton("📖 Help", callback_data="cb_help_start"),
            InlineKeyboardButton("💬 Support", url=SUPPORT_CHAT_URL),
        ],
        [
            InlineKeyboardButton("👨‍💻 Developer", url=DEVELOPER_URL),
            InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true"),
        ],
    ]
    return caption, InlineKeyboardMarkup(buttons)


async def send_start(client: Client, message: Message) -> None:
    """Send the /start panel in private or group chats."""
    is_admin_user = False
    if message.chat.type != ChatType.PRIVATE:
        is_admin_user = await is_admin(client, message)
    markup = await build_start_panel(is_admin_user)
    if PANEL_IMAGE_URL:
        with suppress(Exception):
            await client.send_photo(message.chat.id, PANEL_IMAGE_URL)
    await message.reply_text("Choose an option:", reply_markup=markup)


async def send_control_panel(client: Client, message: Message) -> None:
    """Send the main control panel appropriate for the chat."""
    if message.chat.type == ChatType.PRIVATE:
        caption, markup = await build_private_panel()
    else:
        caption, markup = await build_group_panel(message.chat.id, client)

    try:
        if PANEL_IMAGE_URL:
            await client.send_photo(
                chat_id=message.chat.id,
                photo=PANEL_IMAGE_URL,
                caption=caption,
                reply_markup=markup,
                parse_mode=ParseMode.HTML,
            )
        else:
            await message.reply_text(caption, reply_markup=markup, parse_mode=ParseMode.HTML)
    except Exception as exc:
        logger.warning("Banner failed: %s", exc)
        await message.reply_text(caption, reply_markup=markup, parse_mode=ParseMode.HTML)
