import logging
from time import perf_counter
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from utils.errors import catch_errors
from utils.perms import is_admin
from utils.db import get_setting, set_setting, toggle_setting
from .settings import build_group_panel, build_start_panel

logger = logging.getLogger(__name__)

COMMANDS = [
    ("✅ /approve", "Approve a user"),
    ("❌ /unapprove", "Revoke approval"),
    ("📋 /viewapproved", "List approved users"),
    ("🕒 /setautodelete", "Set auto delete time"),
    ("🔄 /autodeleteon | /autodeleteoff", "Toggle auto delete"),
    ("📝 /autodeleteedited on | off", "Delete edited messages"),
    ("🤐 /mute", "Mute user"),
    ("🚫 /kick", "Kick user"),
    ("🔨 /ban", "Ban user"),
    ("🌐 /biolink on | off", "Filter bio links"),
    ("🔗 /linkfilter on | off", "Filter any link"),
]


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
            await query.message.reply_text(f"🎉 Pong! <code>{latency}ms</code>", parse_mode=ParseMode.HTML)

        elif data in {"cb_help_start", "cb_help_panel"}:
            await query.answer()
            rows = [f"{cmd} - {desc}" for cmd, desc in COMMANDS]
            help_text = "<b>📚 Commands</b>\n\n" + "\n".join(rows)
            back_cb = "cb_start" if data == "cb_help_start" else "cb_back_panel"
            markup = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data=back_cb)]])
            await query.message.edit_text(help_text, reply_markup=markup, parse_mode=ParseMode.HTML)

        elif data == "cb_start":
            await query.answer()
            markup = await build_start_panel(await is_admin(client, query.message))
            await query.message.edit_text("Choose an option:", reply_markup=markup)

        elif data in {"cb_open_panel", "cb_back_panel"}:
            await query.answer()
            caption, markup = await build_group_panel(chat_id, client)
            await query.message.edit_text(caption, reply_markup=markup, parse_mode=ParseMode.HTML)

        elif data.startswith("cb_toggle_"):
            feature_map = {
                "cb_toggle_biolink": "biolink",
                "cb_toggle_autodel": "autodelete",
                "cb_toggle_linkfilter": "linkfilter",
                "cb_toggle_editmode": "editmode",
            }

            feature = feature_map.get(data)
            if not feature:
                await query.answer("⚠️ Unknown toggle.", show_alert=True)
                return

            if not await is_admin(client, query.message, user_id):
                await query.answer("🔒 Admins only!", show_alert=True)
                return

            # Handle auto-delete interval logic separately
            if feature == "autodelete":
                current = await get_setting(chat_id, "autodelete", "0")
                new_value = "0" if current == "1" else "1"
                await set_setting(chat_id, "autodelete", new_value)
                await set_setting(chat_id, "autodelete_interval", "60" if new_value == "1" else "0")
                status = "ENABLED ✅" if new_value == "1" else "DISABLED ❌"
                await query.answer(f"Auto-Delete is now {status}")
            else:
                state = await toggle_setting(chat_id, feature)
                label = feature.replace("filter", " Filter").title()
                await query.answer(f"{label} is now {'ON ✅' if state == '1' else 'OFF ❌'}")

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
            await query.answer("⚠️ Unknown callback", show_alert=True)
