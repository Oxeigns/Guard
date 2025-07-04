"""Modernized basic bot commands with styled replies and buttons."""

import logging
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatType
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions

from utils.perms import is_admin
from utils.errors import catch_errors
from utils.db import toggle_bio_filter, set_bio_filter

logger = logging.getLogger(__name__)

def register(app: Client) -> None:

    # 🔹 /help command (DM only) with modern UI
    @app.on_message(filters.command("help"))
    @catch_errors
    async def help_cmd(client: Client, message: Message):
        logger.info("/help from %s", message.chat.id)
        if message.chat.type != ChatType.PRIVATE:
            await message.reply_text("ℹ️ <b>Please message me in private for help.</b>", parse_mode=ParseMode.HTML)
            return

        help_text = (
            "<b>🛠️ Bot Commands</b>\n\n"
            "/approve - Approve user\n"
            "/unapprove - Revoke approval\n"
            "/viewapproved - List all approved users\n"
            "/setautodelete <sec> - Enable timed auto-deletion\n"
            "/mute - Mute the replied user\n"
            "/kick - Kick the replied user\n"
            "/ban - Ban the replied user\n"
            "/biolink [on|off] - Toggle bio filter\n"
            "/start - Show control panel\n"
        )

        await message.reply_text(
            help_text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Approve Users", callback_data="approve_help")],
                [InlineKeyboardButton("🔐 Admin Panel", callback_data="panel_help")]
            ])
        )

    # 🔹 /auth command - status in group
    @app.on_message(filters.command("auth"))
    @catch_errors
    async def auth_cmd(client: Client, message: Message):
        if message.chat.type == ChatType.PRIVATE:
            await message.reply_text("❌ This command is only for groups.")
            return
        try:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            await message.reply_text(f"🔍 Your status: <code>{member.status}</code>", parse_mode=ParseMode.HTML)
        except Exception as e:
            logger.warning("auth check failed: %s", e)
            await message.reply_text("⚠️ Failed to fetch your status.", parse_mode=ParseMode.HTML)

    # 🔹 Callback handler for buttons
    @app.on_callback_query(filters.regex("^help_tab$"))
    @catch_errors
    async def help_cb(client: Client, query: CallbackQuery):
        await query.message.edit_text(
            "<b>Help Overview:</b>\nUse the buttons or type /help to see command list.",
            parse_mode=ParseMode.HTML
        )

    async def require_admin(client: Client, message: Message) -> bool:
        if not await is_admin(client, message):
            await message.reply_text("🚫 You must be an admin to do this.", parse_mode=ParseMode.HTML)
            return False
        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.reply_text("📌 Reply to a user's message to target them.", parse_mode=ParseMode.HTML)
            return False
        return True

    @app.on_message(filters.command("mute") & filters.group)
    @catch_errors
    async def mute_cmd(client: Client, message: Message):
        if not await require_admin(client, message): return
        user = message.reply_to_message.from_user
        try:
            await client.restrict_chat_member(message.chat.id, user.id, ChatPermissions())
            await message.reply_text(f"🔇 Muted <code>{user.id}</code>", parse_mode=ParseMode.HTML)
        except Exception as e:
            logger.warning("mute failed: %s", e)
            await message.reply_text("⚠️ Couldn't mute. Check my permissions.", parse_mode=ParseMode.HTML)

    @app.on_message(filters.command("kick") & filters.group)
    @catch_errors
    async def kick_cmd(client: Client, message: Message):
        if not await require_admin(client, message): return
        user = message.reply_to_message.from_user
        try:
            await client.ban_chat_member(message.chat.id, user.id)
            await client.unban_chat_member(message.chat.id, user.id)
            await message.reply_text(f"👢 Kicked <code>{user.id}</code>", parse_mode=ParseMode.HTML)
        except Exception as e:
            logger.warning("kick failed: %s", e)
            await message.reply_text("⚠️ Couldn't kick. Check my permissions.", parse_mode=ParseMode.HTML)

    @app.on_message(filters.command("ban") & filters.group)
    @catch_errors
    async def ban_cmd(client: Client, message: Message):
        if not await require_admin(client, message): return
        user = message.reply_to_message.from_user
        try:
            await client.ban_chat_member(message.chat.id, user.id)
            await message.reply_text(f"⛔ Banned <code>{user.id}</code>", parse_mode=ParseMode.HTML)
        except Exception as e:
            logger.warning("ban failed: %s", e)
            await message.reply_text("⚠️ Couldn't ban. Check my permissions.", parse_mode=ParseMode.HTML)

    @app.on_message(filters.command("biolink") & filters.group)
    @catch_errors
    async def biolink_cmd(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text("🔒 Only admins can toggle bio link filtering.", parse_mode=ParseMode.HTML)
            return

        if len(message.command) == 1:
            enabled = await toggle_bio_filter(message.chat.id)
        else:
            arg = message.command[1].lower()
            if arg in {"on", "enable", "true"}:
                await set_bio_filter(message.chat.id, True)
                enabled = True
            elif arg in {"off", "disable", "false"}:
                await set_bio_filter(message.chat.id, False)
                enabled = False
            else:
                await message.reply_text("❗ Usage: /biolink [on|off]", parse_mode=ParseMode.HTML)
                return

        await message.reply_text(
            f"🧬 Bio link filter is now <b>{'ENABLED ✅' if enabled else 'DISABLED ❌'}</b>",
            parse_mode=ParseMode.HTML
        )
