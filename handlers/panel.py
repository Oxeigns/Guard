"""Cleaned settings panel showing only available features."""

import logging
from pyrogram import Client, filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from config import BANNER_URL
from utils.perms import is_admin
from utils.errors import catch_errors

logger = logging.getLogger(__name__)

SETTINGS_PANEL = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("✅ Approve", callback_data="cb_approve"),
        InlineKeyboardButton("🚫 Unapprove", callback_data="cb_unapprove"),
    ],
    [
        InlineKeyboardButton("🗑️ AutoDelete", callback_data="cb_autodel"),
        InlineKeyboardButton("🔗 Toggle Bio Filter", callback_data="cb_biolink_toggle"),
    ],
    [
        InlineKeyboardButton("📖 Help", callback_data="help"),
        InlineKeyboardButton("📡 Ping", callback_data="ping"),
    ],
    [
        InlineKeyboardButton("✅ Close", callback_data="close"),
    ]
])


def register(app: Client) -> None:

    @app.on_message(filters.command("panel"))
    @catch_errors
    async def open_panel(client: Client, message: Message):
        logger.info("/panel from %s", message.chat.id)

        if message.chat.type == ChatType.PRIVATE or await is_admin(client, message):
            group_name = message.chat.title or "this chat"
            caption = (
                "🔧 <b>SETTINGS PANEL</b>\n"
                "Select a setting you want to configure.\n\n"
                f"Group: <code>{group_name}</code>"
            )
            if BANNER_URL:
                try:
                    await message.reply_photo(
                        photo=BANNER_URL,
                        caption=caption,
                        reply_markup=SETTINGS_PANEL,
                        parse_mode=ParseMode.HTML,
                    )
                    return
                except Exception as e:
                    logger.warning("Banner image failed: %s", e)

            await message.reply_text(
                caption,
                reply_markup=SETTINGS_PANEL,
                parse_mode=ParseMode.HTML
            )
        else:
            await message.reply_text("❌ Only admins can access this panel.", parse_mode=ParseMode.HTML)

    @app.on_callback_query(filters.regex("^panel_open$"))
    @catch_errors
    async def open_panel_from_menu(client: Client, query: CallbackQuery):
        if not await is_admin(client, query.message, query.from_user.id):
            await query.answer("Admins only!", show_alert=True)
            return

        group_name = query.message.chat.title or "this group"
        caption = (
            "🔧 <b>SETTINGS PANEL</b>\n"
            "Select a setting you want to configure.\n\n"
            f"Group: <code>{group_name}</code>"
        )

        await query.answer()
        try:
            if query.message.photo:
                await query.message.edit_caption(
                    caption, reply_markup=SETTINGS_PANEL, parse_mode=ParseMode.HTML
                )
            else:
                await query.message.edit_text(
                    caption, reply_markup=SETTINGS_PANEL, parse_mode=ParseMode.HTML
                )
        except Exception as e:
            logger.warning("Edit failed: %s", e)

    @app.on_callback_query(filters.regex("^cb_(approve|unapprove|autodel|biolink_toggle)$"))
    @catch_errors
    async def placeholder_buttons(client: Client, query: CallbackQuery):
        await query.answer()
        await query.message.reply_text(
            f"ℹ️ Use the respective command like <code>/{query.data[3:]}</code> in the group.",
            parse_mode=ParseMode.HTML
        )

    @app.on_callback_query(filters.regex("^close$"))
    @catch_errors
    async def close_panel(client: Client, query: CallbackQuery):
        await query.message.delete()
