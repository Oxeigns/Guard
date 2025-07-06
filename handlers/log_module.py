import logging
from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config import SUPPORT_CHAT_URL, DEVELOPER_URL
from utils.errors import catch_errors
from utils.db import (
    set_bio_filter, get_bio_filter,
    get_setting, set_setting
)
from utils.messages import safe_edit_message
from handlers.panels import send_start, get_help_keyboard, build_settings_panel

logger = logging.getLogger(__name__)

# Help section content for buttons
HELP_SECTIONS = {
    "help_biomode": (
        "🛡️ <b>BioMode</b>\n"
        "Scans bios of new users for suspicious content like links.\n"
        "Use <code>/biolink on|off</code> to toggle."
    ),
    "help_autodelete": (
        "🧹 <b>AutoDelete</b>\n"
        "Deletes non-admin messages after a set delay.\n"
        "Set delay using <code>/setautodelete &lt;seconds&gt;</code>."
    ),
    "help_linkfilter": (
        "🔗 <b>LinkFilter</b>\n"
        "Deletes URLs from non-admin messages.\n"
        "Toggle using <code>/linkfilter on|off</code>."
    ),
    "help_editmode": (
        "✏️ <b>EditMode</b>\n"
        "Deletes edited messages by normal users.\n"
        "Use <code>/editfilter on|off</code>."
    ),
    "help_broadcast": (
        "📢 <b>Broadcast</b>\n"
        "Owner-only broadcast to groups via <code>/broadcast</code>."
    ),
}


def register(app: Client) -> None:
    logger.info("✅ Registered: callbacks.py")

    @app.on_callback_query()
    @catch_errors
    async def handle_callback(client: Client, query: CallbackQuery):
        data = query.data
        user_id = query.from_user.id
        chat_id = query.message.chat.id if query.message else "N/A"

        logger.debug(f"[CALLBACK] From user {user_id} in chat {chat_id} → data: {data}")

        if data in {"cb_start", "cb_back_panel"}:
            await query.answer()
            await send_start(client, query.message, include_back=(data == "cb_back_panel"))

        elif data == "open_settings":
            await query.answer()
            await _render_settings_panel(query)

        elif data.startswith("toggle_"):
            await query.answer("Toggled ✅")
            await _handle_toggle(data, query.message.chat.id)
            await _render_settings_panel(query)

        elif data in {"cb_help_start", "cb_help_panel"}:
            await query.answer()
            await safe_edit_message(
                query.message,
                caption="📘 <b>Command Help</b>\n\nUse the buttons below to learn more.",
                reply_markup=get_help_keyboard("cb_start"),
                parse_mode=ParseMode.HTML,
            )

        elif data in HELP_SECTIONS:
            await query.answer()
            await safe_edit_message(
                query.message,
                caption=HELP_SECTIONS[data],
                reply_markup=get_help_keyboard("cb_help_start"),
                parse_mode=ParseMode.HTML,
            )

        elif data == "help_support":
            await query.answer()
            await safe_edit_message(
                query.message,
                caption="🆘 <b>Need help?</b>",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔗 Join Support", url=SUPPORT_CHAT_URL)],
                    [InlineKeyboardButton("🔙 Back", callback_data="cb_help_start")]
                ]),
                parse_mode=ParseMode.HTML,
            )

        elif data == "help_developer":
            await query.answer()
            await safe_edit_message(
                query.message,
                caption="👨‍💻 <b>Developer Info</b>",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✉️ Message Developer", url=DEVELOPER_URL)],
                    [InlineKeyboardButton("🔙 Back", callback_data="cb_help_start")]
                ]),
                parse_mode=ParseMode.HTML,
            )

        else:
            logger.warning(f"⚠️ Unknown callback data received: {data}")
            await query.answer("⚠️ Unknown action", show_alert=True)


# 🔁 Update the group settings panel
async def _render_settings_panel(query: CallbackQuery):
    chat_id = query.message.chat.id
    markup = await build_settings_panel(chat_id)
    await safe_edit_message(
        query.message,
        caption="⚙️ <b>Group Settings</b>",
        reply_markup=markup,
        parse_mode=ParseMode.HTML,
    )


# ⚙️ Toggle settings and update DB
async def _handle_toggle(data: str, chat_id: int):
    if data == "toggle_biolink":
        current = await get_bio_filter(chat_id)
        await set_bio_filter(chat_id, not current)

    elif data == "toggle_linkfilter":
        current = str(await get_setting(chat_id, "linkfilter", "0")) == "1"
        await set_setting(chat_id, "linkfilter", "0" if current else "1")

    elif data == "toggle_editfilter":
        current = str(await get_setting(chat_id, "editmode", "0")) == "1"
        await set_setting(chat_id, "editmode", "0" if current else "1")

    elif data == "toggle_autodelete":
        delay = int(await get_setting(chat_id, "autodelete_interval", "0") or 0)
        await set_setting(chat_id, "autodelete_interval", "0" if delay else "30")

    else:
        logger.warning(f"🛑 Unrecognized toggle key: {data}")
