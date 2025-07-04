"""Enhanced user approval system with modern UI feedback and cleaner logic."""

import logging
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from utils.db import (
    approve_user, unapprove_user, get_approved,
    is_approved, get_approval_mode, toggle_approval_mode,
    set_approval_mode
)
from utils.perms import is_admin
from utils.errors import catch_errors

logger = logging.getLogger(__name__)


def user_mention(user) -> str:
    return f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"


def register(app: Client) -> None:

    async def require_admin_reply(message: Message, action: str) -> tuple[int, str] | None:
        if not await is_admin(app, message):
            await message.reply_text("🚫 Only admins can do this.", parse_mode=ParseMode.HTML)
            return None
        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.reply_text(f"📌 Reply to a user's message to {action}.", parse_mode=ParseMode.HTML)
            return None
        user = message.reply_to_message.from_user
        return user.id, user_mention(user)

    @app.on_message(filters.command("approve") & filters.group)
    @catch_errors
    async def approve_cmd(client: Client, message: Message):
        result = await require_admin_reply(message, "approve")
        if result is None: return
        user_id, mention = result
        await approve_user(message.chat.id, user_id)
        await message.reply_text(f"✅ Approved {mention}", parse_mode=ParseMode.HTML)

    @app.on_message(filters.command("unapprove") & filters.group)
    @catch_errors
    async def unapprove_cmd(client: Client, message: Message):
        result = await require_admin_reply(message, "unapprove")
        if result is None: return
        user_id, mention = result
        await unapprove_user(message.chat.id, user_id)
        await message.reply_text(f"❌ Unapproved {mention}", parse_mode=ParseMode.HTML)

    @app.on_message(filters.command("viewapproved") & filters.group)
    @catch_errors
    async def view_approved(client: Client, message: Message):
        if not await is_admin(app, message):
            await message.reply_text("🚫 Only admins can view approvals.", parse_mode=ParseMode.HTML)
            return

        users = await get_approved(message.chat.id)
        if not users:
            await message.reply_text("📭 No approved users found.", parse_mode=ParseMode.HTML)
            return

        user_list = "\n".join(f"• <code>{uid}</code>" for uid in users)
        await message.reply_text(
            f"<b>📋 Approved Users:</b>\n{user_list}",
            parse_mode=ParseMode.HTML
        )

    @app.on_message(filters.command("approval") & filters.group)
    @catch_errors
    async def approval_mode_cmd(client: Client, message: Message):
        if not await is_admin(app, message):
            await message.reply_text("🔒 You must be an admin to change approval mode.", parse_mode=ParseMode.HTML)
            return

        if len(message.command) == 1:
            enabled = await toggle_approval_mode(message.chat.id)
        else:
            mode = message.command[1].lower()
            if mode in {"on", "enable", "true"}:
                await set_approval_mode(message.chat.id, True)
                enabled = True
            elif mode in {"off", "disable", "false"}:
                await set_approval_mode(message.chat.id, False)
                enabled = False
            else:
                await message.reply_text("❗ Usage: /approval [on|off]", parse_mode=ParseMode.HTML)
                return

        await message.reply_text(
            f"🔄 Approval mode is now <b>{'ENABLED ✅' if enabled else 'DISABLED ❌'}</b>",
            parse_mode=ParseMode.HTML
        )

    @app.on_message(filters.group, group=10)
    @catch_errors
    async def enforce_approval(client: Client, message: Message):
        user = message.from_user
        chat_id = message.chat.id

        if not user or user.is_bot:
            return

        if await is_admin(client, message, user.id):
            return

        if not await get_approval_mode(chat_id):
            return

        if await is_approved(chat_id, user.id):
            return

        try:
            await message.delete()
            logger.info("Deleted message from unapproved user %s in chat %s", user.id, chat_id)
        except Exception as e:
            logger.warning("Failed to delete unapproved message: %s", e)
