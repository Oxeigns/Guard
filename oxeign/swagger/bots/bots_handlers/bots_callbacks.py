import logging
from contextlib import suppress
from time import perf_counter

from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config import SUPPORT_CHAT_URL, DEVELOPER_URL
from utils.errors import catch_errors
from utils.perms import is_admin
from utils.messages import safe_edit_message
from .panels import (
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

        logger.debug("Callback triggered: %s", data)

        # ⏱ Ping response
        if data == "cb_ping":
            start = perf_counter()
            await query.answer("📡 Pinging...")
            latency = round((perf_counter() - start) * 1000, 2)
            await query.message.reply_text(
                f"🎉 Pong! <code>{latency}ms</code>", parse_mode=ParseMode.HTML
            )

        # ❌ Close current message
        elif data == "cb_close":
            await query.answer()
            with suppress(Exception):
                await query.message.delete()

        # 🔁 Load main control/start panel
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
                await safe_edit_message(
                    query.message,
                    text=caption,
                    reply_markup=markup,
                    parse_mode=ParseMode.HTML,
                )

        # ✅ Approve help tip
        elif data == "cb_approve":
            await query.answer()
            await query.message.reply_text(
                "✅ Reply to a user with <code>/approve</code> to approve them.",
                parse_mode=ParseMode.HTML,
            )

        # ❌ Unapprove help tip
        elif data == "cb_unapprove":
            await query.answer()
            await query.message.reply_text(
                "❌ Reply to a user with <code>/unapprove</code> to unapprove them.",
                parse_mode=ParseMode.HTML,
            )

        # 🔇 Filter unmute placeholders (disabled)
        elif data.startswith("biofilter_unmute_") or data.startswith("linkfilter_unmute_"):
            await query.answer("❌ Manual unmute is disabled.\nAsk an admin.", show_alert=True)

        # 📘 Help command list panel
        elif data in {"cb_help_start", "cb_help_panel"}:
            commands_text = "\n".join([f"{cmd} - {desc}" for cmd, desc in COMMANDS])
            back_cb = "cb_start" if data == "cb_help_start" else "cb_back_panel"
            await safe_edit_message(
                query.message,
                caption=f"<b>📚 Commands</b>\n\n{commands_text}\n\n👇 Tap the buttons below to view module help:",
                reply_markup=get_help_keyboard(back_cb),
                parse_mode=ParseMode.HTML,
            )
            return await query.answer()

        # 📖 BioMode Help
        elif data == "help_biomode":
            await safe_edit_message(
                query.message,
                caption=(
                    "🛡 <b>BioMode</b>\n\n"
                    "Monitors user bios and deletes messages if they contain URLs.\n\n"
                    "<b>Usage:</b>\n"
                    "➤ <code>/biolink on</code>\n"
                    "➤ <code>/biolink off</code>\n\n"
                    "🚫 Blocks users with links in bio from messaging.\n"
                    "👮 Admins only."
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="cb_help_start")]
                ]),
                parse_mode=ParseMode.HTML,
            )
            return await query.answer()

        # 🧹 AutoDelete Help
        elif data == "help_autodelete":
            await safe_edit_message(
                query.message,
                caption=(
                    "🧹 <b>AutoDelete</b>\n\n"
                    "Removes messages after a delay.\n\n"
                    "<b>Usage:</b>\n"
                    "➤ <code>/setautodelete 30</code> – delete after 30s\n"
                    "➤ <code>/setautodelete 0</code> – disable\n\n"
                    "🧼 Keeps your chat clean automatically."
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="cb_help_start")]
                ]),
                parse_mode=ParseMode.HTML,
            )
            return await query.answer()

        # 🔗 LinkFilter Help
        elif data == "help_linkfilter":
            await safe_edit_message(
                query.message,
                caption=(
                    "🔗 <b>LinkFilter</b>\n\n"
                    "Blocks messages with links from non-admins.\n\n"
                    "<b>Usage:</b>\n"
                    "➤ <code>/linkfilter on</code>\n"
                    "➤ <code>/linkfilter off</code>\n\n"
                    "🔒 Stops spam and scam links."
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="cb_help_start")]
                ]),
                parse_mode=ParseMode.HTML,
            )
            return await query.answer()

        # ✏️ EditMode Help
        elif data == "help_editmode":
            await safe_edit_message(
                query.message,
                caption=(
                    "✏️ <b>EditMode</b>\n\n"
                    "Auto-removes edited messages.\n\n"
                    "No command needed.\n\n"
                    "🔍 Prevents stealth spam edits."
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="cb_help_start")]
                ]),
                parse_mode=ParseMode.HTML,
            )
            return await query.answer()

        # 🆘 Support
        elif data == "help_support":
            await safe_edit_message(
                query.message,
                caption="🆘 <b>Need help?</b>\n\nJoin our support group for assistance and community help.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔗 Join Support", url=SUPPORT_CHAT_URL)],
                    [InlineKeyboardButton("🔙 Back", callback_data="cb_help_start")]
                ]),
                parse_mode=ParseMode.HTML,
            )
            return await query.answer()

        # 👨‍💻 Developer
        elif data == "help_developer":
            await safe_edit_message(
                query.message,
                caption="👨‍💻 <b>Developer Info</b>\n\nGot feedback or questions? Contact the developer directly.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✉️ Message Developer", url=DEVELOPER_URL)],
                    [InlineKeyboardButton("🔙 Back", callback_data="cb_help_start")]
                ]),
                parse_mode=ParseMode.HTML,
            )
            return await query.answer()

        # ⚠️ Unknown callback
        else:
            await query.answer("⚠️ Unknown callback", show_alert=True)
