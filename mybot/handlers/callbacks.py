import logging
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from ..config import SUPPORT_CHAT_URL, DEVELOPER_URL
from ..utils.errors import catch_errors
from ..utils.db import (
    set_bio_filter, get_bio_filter,
    get_setting, set_setting
)
from ..utils.messages import safe_edit_message
from .panels import send_start, get_help_keyboard, build_settings_panel

logger = logging.getLogger(__name__)

help_sections = {
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

    @app.on_callback_query()
    @catch_errors
    async def callbacks(client: Client, query: CallbackQuery):
        data = query.data
        chat_id = query.message.chat.id

        logger.debug("[CALLBACK] %s from %s in chat %s", data, query.from_user.id, chat_id)

        if data in {"cb_start", "cb_back_panel"}:
            await query.answer()
            await send_start(client, query.message, include_back=data == "cb_back_panel")

        elif data == "open_settings":
            await query.answer()
            markup = await build_settings_panel(chat_id)
            await safe_edit_message(
                query.message,
                caption="⚙️ <b>Group Settings</b>",
                reply_markup=markup,
                parse_mode=ParseMode.HTML
            )

        elif data == "toggle_biolink":
            current = await get_bio_filter(chat_id)
            await set_bio_filter(chat_id, not current)
            await _update_settings_panel(query, chat_id)

        elif data == "toggle_linkfilter":
            current = str(await get_setting(chat_id, "linkfilter", "0")) == "1"
            await set_setting(chat_id, "linkfilter", "0" if current else "1")
            await _update_settings_panel(query, chat_id)

        elif data == "toggle_editfilter":
            current = str(await get_setting(chat_id, "editmode", "0")) == "1"
            await set_setting(chat_id, "editmode", "0" if current else "1")
            await _update_settings_panel(query, chat_id)

        elif data == "toggle_autodelete":
            delay = int(await get_setting(chat_id, "autodelete_interval", "0") or 0)
            new_delay = "0" if delay else "30"
            await set_setting(chat_id, "autodelete_interval", new_delay)
            await _update_settings_panel(query, chat_id)

        elif data in {"cb_help_start", "cb_help_panel"}:
            await query.answer()
            await safe_edit_message(
                query.message,
                caption="<b>📚 Commands</b>\n\nUse the buttons for module help.",
                reply_markup=get_help_keyboard("cb_start"),
                parse_mode=ParseMode.HTML,
            )

        elif data in help_sections:
            await query.answer()
            await safe_edit_message(
                query.message,
                caption=help_sections[data],
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
            logger.warning("⚠️ Unknown callback data: %s", data)
            await query.answer("⚠️ Unknown action", show_alert=True)


# Helper to refresh the settings panel
async def _update_settings_panel(query: CallbackQuery, chat_id: int):
    await query.answer("Toggled")
    markup = await build_settings_panel(chat_id)
    await safe_edit_message(
        query.message,
        caption="⚙️ <b>Group Settings</b>",
        reply_markup=markup,
        parse_mode=ParseMode.HTML,
    )
