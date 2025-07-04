import logging
from time import perf_counter
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from utils.errors import catch_errors
from utils.perms import is_admin
from utils.db import get_setting, set_setting, toggle_setting
from panel import build_group_panel

logger = logging.getLogger(__name__)


def register(app: Client) -> None:
    @app.on_callback_query()
    @catch_errors
    async def callback_handler(client: Client, query: CallbackQuery):
        data = query.data
        chat_id = query.message.chat.id
        user_id = query.from_user.id

        if data == "cb_ping":
            start = perf_counter()
            await query.answer("📡 Pinging...")
            latency = round((perf_counter() - start) * 1000, 2)
            await query.message.reply_text(
                f"🎉 Pong! <code>{latency}ms</code>", parse_mode=ParseMode.HTML
            )

        elif data == "cb_help":
            await query.answer()
            help_text = (
                "<b>📖 Bot Commands</b>\n\n"
                "/approve – Approve user\n"
                "/unapprove – Revoke approval\n"
                "/viewapproved – List approved users\n"
                "/setautodelete <seconds>\n"
                "/autodeleteon | /autodeleteoff\n"
                "/mute | /kick | /ban\n"
                "/biolink on/off – Toggle bio link filter"
            )
            markup = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="cb_back")]])
            await query.message.edit_text(help_text, reply_markup=markup, parse_mode=ParseMode.HTML)

        elif data == "cb_back":
            await query.answer()
            caption, markup = await build_group_panel(chat_id, client)
            await query.message.edit_text(caption, reply_markup=markup, parse_mode=ParseMode.HTML)

        elif data == "cb_toggle_biolink":
            if not await is_admin(client, query.message, user_id):
                await query.answer("Admins only!", show_alert=True)
                return
            state = await toggle_setting(chat_id, "biolink")
            await query.answer(f"Bio Filter is now {'ON ✅' if state == '1' else 'OFF ❌'}")
            caption, markup = await build_group_panel(chat_id, client)
            await query.message.edit_text(caption, reply_markup=markup, parse_mode=ParseMode.HTML)

        elif data == "cb_toggle_autodel":
            if not await is_admin(client, query.message, user_id):
                await query.answer("Admins only!", show_alert=True)
                return
            current = await get_setting(chat_id, "autodelete", "0")
            new_value = "0" if current == "1" else "1"
            await set_setting(chat_id, "autodelete", new_value)
            await set_setting(chat_id, "autodelete_interval", "60" if new_value == "1" else "0")
            await query.answer(
                f"Auto-Delete is now {'ENABLED ✅' if new_value == '1' else 'DISABLED ❌'}"
            )
            caption, markup = await build_group_panel(chat_id, client)
            await query.message.edit_text(caption, reply_markup=markup, parse_mode=ParseMode.HTML)

        elif data == "cb_approve":
            await query.answer()
            await query.message.reply_text(
                "✅ Reply to a user with <code>/approve</code> to approve them.",
                parse_mode=ParseMode.HTML,
            )

        elif data == "cb_unapprove":
            await query.answer()
            await query.message.reply_text(
                "🚫 Reply to a user with <code>/unapprove</code> to unapprove them.",
                parse_mode=ParseMode.HTML,
            )

        else:
            await query.answer("Unknown command", show_alert=True)
