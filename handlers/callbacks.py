import logging
from contextlib import suppress
from time import perf_counter
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions

from utils.errors import catch_errors
from utils.perms import is_admin
from utils.db import toggle_setting
from utils.messages import safe_edit_message
from .settings import build_group_panel, build_start_panel

logger = logging.getLogger(__name__)

COMMANDS = [
    ("✅ /approve", "Approve a user"),
    ("❌ /unapprove", "Revoke approval"),
    ("📋 /viewapproved", "List approved users"),
    ("🕒 /setautodelete <seconds>", "Enable auto delete"),
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
            markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=back_cb)]])
            await safe_edit_message(
                query.message,
                text=help_text,
                reply_markup=markup,
                parse_mode=ParseMode.HTML,
            )

        elif data == "cb_close":
            await query.answer()
            with suppress(Exception):
                await query.message.delete()

        elif data == "cb_start":
            await query.answer()
            markup = await build_start_panel(await is_admin(client, query.message))
            await safe_edit_message(query.message, text="Choose an option:", reply_markup=markup)

        elif data in {"cb_open_panel", "cb_back_panel"}:
            await query.answer()
            caption, markup = await build_group_panel(chat_id, client)
            await safe_edit_message(query.message, text=caption, reply_markup=markup, parse_mode=ParseMode.HTML)

        elif data.startswith("cb_toggle_"):
            feature_map = {
                "cb_toggle_biolink": "biolink",
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

            state = await toggle_setting(chat_id, feature)
            label = feature.replace("filter", " Filter").title()
            await query.answer(f"{label} is now {'ON ✅' if state == '1' else 'OFF ❌'}")

            caption, markup = await build_group_panel(chat_id, client)
            await safe_edit_message(query.message, text=caption, reply_markup=markup, parse_mode=ParseMode.HTML)

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

        # ✅ Fixed: Unmute button handler for bio/link filters
        elif data.startswith("biofilter_unmute_") or data.startswith("linkfilter_unmute_"):
            target_id = int(data.split("_")[-1])
            if not await is_admin(client, query.message, query.from_user.id):
                await query.answer("🔒 Only admins can unmute users.", show_alert=True)
                return

            try:
                await client.restrict_chat_member(
                    query.message.chat.id,
                    target_id,
                    ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_polls=True,
                        can_send_other_messages=True,
                        can_add_web_page_previews=True,
                        can_invite_users=True,
                    )
                )
                await query.answer("✅ User unmuted.")
                await query.message.reply_text(
                    f"🔓 User <a href='tg://user?id={target_id}'>unmuted</a>.",
                    parse_mode=ParseMode.HTML,
                )
            except Exception as e:
                logger.error("Failed to unmute user %s: %s", target_id, e)
                await query.answer("❌ Failed to unmute user.", show_alert=True)

        else:
            await query.answer("⚠️ Unknown callback", show_alert=True)
