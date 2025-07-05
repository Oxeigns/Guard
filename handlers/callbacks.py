import logging

from pyrogram import Client, filters
from utils.errors import catch_errors
from pyrogram.enums import ParseMode
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from utils.messages import safe_edit_message
from utils.db import set_bio_filter, set_setting, get_setting, get_bio_filter
from config import SUPPORT_CHAT_URL, DEVELOPER_URL
from .panels import send_start, get_help_keyboard, build_settings_panel

logger = logging.getLogger(__name__)

help_sections = {
    "help_biomode": (
        "🛡️ <b>BioMode</b>\n"
        "Enables scanning of user bios when they join. If the bio contains a link "
        "or is unusually long, the join message is deleted and the user is warned.\n"
        "Use <code>/biolink on|off</code> to toggle."
    ),
    "help_autodelete": (
        "🧹 <b>AutoDelete</b>\n"
        "Automatically removes all non-admin messages after the configured delay.\n"
        "Set the delay with <code>/setautodelete &lt;seconds&gt;</code>. Use 0 to disable."
    ),
    "help_linkfilter": (
        "🔗 <b>LinkFilter</b>\n"
        "Deletes messages containing URLs from non-admin users. Useful against spam links.\n"
        "Turn on or off with <code>/linkfilter on|off</code>."
    ),
    "help_editmode": (
        "✏️ <b>EditMode</b>\n"
        "Deletes edited messages from regular users. This prevents stealth editing of spam.\n"
        "Toggle using <code>/editfilter on|off</code>."
    ),
    "help_broadcast": (
        "📢 <b>Broadcast</b>\n"
        "Send a message to every group I've joined.\n"
        "Only the owner can use <code>/broadcast &lt;text&gt;</code>."
    ),
}


def register(app: Client) -> None:
    print("✅ Registered: callbacks.py")
    ...
    @app.on_callback_query()
    @catch_errors
    async def callbacks(client: Client, query: CallbackQuery):
        data = query.data
        logger.debug("[CALLBACK] %s from %s in %s", data, query.from_user.id, query.message.chat.id)
        if data in {"cb_start", "cb_back_panel"}:
            await query.answer()
            await send_start(client, query.message, include_back=data == "cb_back_panel")
        elif data == "open_settings":
            await query.answer()
            markup = await build_settings_panel(query.message.chat.id)
            await safe_edit_message(query.message, caption="⚙️ <b>Group Settings</b>", reply_markup=markup, parse_mode=ParseMode.HTML)
        elif data == "toggle_biolink":
            current = await get_bio_filter(query.message.chat.id)
            await set_bio_filter(query.message.chat.id, not current)
            markup = await build_settings_panel(query.message.chat.id)
            await safe_edit_message(query.message, caption="⚙️ <b>Group Settings</b>", reply_markup=markup, parse_mode=ParseMode.HTML)
            await query.answer("Toggled")
        elif data == "toggle_linkfilter":
            current = str(await get_setting(query.message.chat.id, "linkfilter", "0")) == "1"
            await set_setting(query.message.chat.id, "linkfilter", "0" if current else "1")
            markup = await build_settings_panel(query.message.chat.id)
            await safe_edit_message(query.message, caption="⚙️ <b>Group Settings</b>", reply_markup=markup, parse_mode=ParseMode.HTML)
            await query.answer("Toggled")
        elif data == "toggle_editfilter":
            current = str(await get_setting(query.message.chat.id, "editmode", "0")) == "1"
            await set_setting(query.message.chat.id, "editmode", "0" if current else "1")
            markup = await build_settings_panel(query.message.chat.id)
            await safe_edit_message(query.message, caption="⚙️ <b>Group Settings</b>", reply_markup=markup, parse_mode=ParseMode.HTML)
            await query.answer("Toggled")
        elif data == "toggle_autodelete":
            delay = int(await get_setting(query.message.chat.id, "autodelete_interval", "0") or 0)
            if delay:
                await set_setting(query.message.chat.id, "autodelete_interval", "0")
            else:
                await set_setting(query.message.chat.id, "autodelete_interval", "30")
            markup = await build_settings_panel(query.message.chat.id)
            await safe_edit_message(query.message, caption="⚙️ <b>Group Settings</b>", reply_markup=markup, parse_mode=ParseMode.HTML)
            await query.answer("Updated")
        elif data in {"cb_help_start", "cb_help_panel"}:
            commands_text = "\n".join([f"{k[5:].replace('_',' ').title()}" for k in help_sections])
            back_cb = "cb_start"
            await safe_edit_message(
                query.message,
                caption=f"<b>📚 Commands</b>\n\nUse the buttons for module help.",
                reply_markup=get_help_keyboard(back_cb),
                parse_mode=ParseMode.HTML,
            )
            await query.answer()
        elif data in help_sections:
            await safe_edit_message(
                query.message,
                caption=help_sections[data],
                reply_markup=get_help_keyboard("cb_start"),
                parse_mode=ParseMode.HTML,
            )
            await query.answer()
        elif data == "help_support":
            markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Join Support", url=SUPPORT_CHAT_URL)],
                [InlineKeyboardButton("🔙 Back", callback_data="cb_help_start")],
            ])
            await safe_edit_message(
                query.message,
                caption="🆘 <b>Need help?</b>",
                reply_markup=markup,
                parse_mode=ParseMode.HTML,
            )
            await query.answer()
        elif data == "help_developer":
            markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("✉️ Message Developer", url=DEVELOPER_URL)],
                [InlineKeyboardButton("🔙 Back", callback_data="cb_help_start")],
            ])
            await safe_edit_message(
                query.message,
                caption="👨‍💻 <b>Developer Info</b>",
                reply_markup=markup,
                parse_mode=ParseMode.HTML,
            )
            await query.answer()
        else:
            await query.answer("Unknown")
