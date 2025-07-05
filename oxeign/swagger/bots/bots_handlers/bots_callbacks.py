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
    build_start_panel,
    get_help_keyboard,
    send_start,
)
from .bots_commands import COMMANDS

logger = logging.getLogger(__name__)

# 📘 Help Content Dictionary
help_sections = {
    "help_biomode": (
        "🛡️ <b>BioMode</b>\n\n"
        "Deletes messages from users whose bios contain links or suspicious content.\n"
        "Protects your group from self-promoters.\n\n"
        "<b>Commands:</b>\n"
        "• <code>/biolink on</code> – Enable BioMode\n"
        "• <code>/biolink off</code> – Disable BioMode"
    ),
    "help_autodelete": (
        "🧹 <b>AutoDelete</b>\n\n"
        "Automatically removes messages after a delay to keep the group clean.\n\n"
        "<b>Commands:</b>\n"
        "• <code>/setautodelete 30</code> – Delete after 30s\n"
        "• <code>/setautodelete 0</code> – Disable AutoDelete"
    ),
    "help_linkfilter": (
        "🔗 <b>LinkFilter</b>\n\n"
        "Blocks non-admins from sending links.\n"
        "Useful against spam, scams, and promotions.\n\n"
        "<b>Commands:</b>\n"
        "• <code>/linkfilter on</code>\n"
        "• <code>/linkfilter off</code>"
    ),
    "help_editmode": (
        "✏️ <b>EditMode</b>\n\n"
        "Deletes edited messages instantly.\n"
        "Prevents sneaky edits after posting.\n\n"
        "<i>No commands required – works silently in background.</i>"
    ),
}


def register(app: Client) -> None:
    @app.on_callback_query()  # ✅ Fixed: allow all callback data
    @catch_errors
    async def callback_handler(client: Client, query: CallbackQuery):
        data = query.data
        chat_id = query.message.chat.id

        logger.debug("Callback triggered: %s", data)

        # ⏱ Ping test
        if data == "cb_ping":
            start = perf_counter()
            await query.answer("📡 Pinging...")
            latency = round((perf_counter() - start) * 1000, 2)
            await query.message.reply_text(
                f"🎉 Pong! <code>{latency}ms</code>", parse_mode=ParseMode.HTML
            )

        # ❌ Close button
        elif data == "cb_close":
            await query.answer()
            with suppress(Exception):
                await query.message.delete()

        # 🔁 Reload main panel
        elif data in {"cb_start", "cb_open_panel", "cb_back_panel"}:
            await query.answer()
            await send_start(client, query.message)

        # 🧾 Full command list
        elif data in {"cb_help_start", "cb_help_panel"}:
            commands_text = "\n".join([f"{cmd} - {desc}" for cmd, desc in COMMANDS])
            back_cb = "cb_start" if data == "cb_help_start" else "cb_back_panel"
            await safe_edit_message(
                query.message,
                caption=f"<b>📚 Commands</b>\n\n{commands_text}\n\n👇 Tap below for help on each module:",
                reply_markup=get_help_keyboard(back_cb),
                parse_mode=ParseMode.HTML,
            )
            return await query.answer()

        # ℹ️ Specific module help
        elif data in help_sections:
            await safe_edit_message(
                query.message,
                caption=help_sections[data],
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="cb_help_start")]
                ]),
                parse_mode=ParseMode.HTML,
            )
            return await query.answer()

        # 🆘 Support group
        elif data == "help_support":
            await safe_edit_message(
                query.message,
                caption="🆘 <b>Need help?</b>\n\nJoin our support group below.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔗 Join Support", url=SUPPORT_CHAT_URL)],
                    [InlineKeyboardButton("🔙 Back", callback_data="cb_help_start")]
                ]),
                parse_mode=ParseMode.HTML,
            )
            return await query.answer()

        # 👨‍💻 Developer contact
        elif data == "help_developer":
            await safe_edit_message(
                query.message,
                caption="👨‍💻 <b>Developer Info</b>\n\nFor feature requests or bug reports, contact the developer.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✉️ Message Developer", url=DEVELOPER_URL)],
                    [InlineKeyboardButton("🔙 Back", callback_data="cb_help_start")]
                ]),
                parse_mode=ParseMode.HTML,
            )
            return await query.answer()

        # ✅ Approve user usage tip
        elif data == "cb_approve":
            await query.answer()
            await query.message.reply_text(
                "✅ Reply to a user with <code>/approve</code> to approve them.",
                parse_mode=ParseMode.HTML,
            )

        # ❌ Unapprove user usage tip
        elif data == "cb_unapprove":
            await query.answer()
            await query.message.reply_text(
                "❌ Reply to a user with <code>/unapprove</code> to unapprove them.",
                parse_mode=ParseMode.HTML,
            )

        # 🔇 Disabled manual unmute
        elif data.startswith("biofilter_unmute_") or data.startswith("linkfilter_unmute_"):
            await query.answer("❌ Manual unmute is disabled.\nAsk an admin.", show_alert=True)

        # ⚠️ Unknown fallback
        else:
            await query.answer("⚠️ Unknown callback received.", show_alert=True)
