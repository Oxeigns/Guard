import logging
from contextlib import suppress
from time import perf_counter

from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from utils.errors import catch_errors
from utils.perms import is_admin
from utils.messages import safe_edit_message
from .bots_settings import (
    build_group_panel,
    build_start_panel,
    get_help_keyboard,
)
from .bots_commands import COMMANDS

logger = logging.getLogger(__name__)


def register(app: Client) -> None:
    @app.on_callback_query(filters.regex(r"^cb_"))
    @catch_errors
    async def callback_handler(client: Client, query: CallbackQuery):
        data = query.data
        chat_id = query.message.chat.id
        user_id = query.from_user.id

        logger.debug("Received callback: %s", data)

        # Ping Test
        if data == "cb_ping":
            start = perf_counter()
            await query.answer("📡 Pinging...")
            latency = round((perf_counter() - start) * 1000, 2)
            await query.message.reply_text(
                f"🎉 Pong! <code>{latency}ms</code>", parse_mode=ParseMode.HTML
            )

        # Close Panel
        elif data == "cb_close":
            await query.answer()
            with suppress(Exception):
                await query.message.delete()

        # Main Panel
        elif data in {"cb_start", "cb_open_panel", "cb_back_panel"}:
            await query.answer()
            if query.message.chat.type == "private":
                markup = await build_start_panel(await is_admin(client, query.message))
                await safe_edit_message(
                    query.message,
                    text="⚙️ Settings are available only in groups.\n\nUse this bot in a group to access control panel.",
                    reply_markup=markup,
                    parse_mode=ParseMode.HTML,
                )
            else:
                caption, markup = await build_group_panel(chat_id, client)
                await safe_edit_message(query.message, text=caption, reply_markup=markup, parse_mode=ParseMode.HTML)

        # Toggle Settings (disabled)
        elif data.startswith("cb_toggle_"):
            await query.answer(
                "⚠️ Toggle buttons have been removed. Use commands instead.",
                show_alert=True,
            )

        # Quick Guide Commands
        elif data == "cb_approve":
            await query.answer()
            await query.message.reply_text(
                "✅ Reply to a user with <code>/approve</code> to approve them.",
                parse_mode=ParseMode.HTML,
            )

        elif data == "cb_unapprove":
            await query.answer()
            await query.message.reply_text(
                "❌ Reply to a user with <code>/unapprove</code> to unapprove them.",
                parse_mode=ParseMode.HTML,
            )

        # Deprecated: No unmute buttons in filter.py
        elif data.startswith("biofilter_unmute_") or data.startswith("linkfilter_unmute_"):
            await query.answer("❌ Manual unmute is disabled.\nAsk an admin.", show_alert=True)

        # Unknown Callback
        else:
            await query.answer("⚠️ Unknown callback", show_alert=True)
