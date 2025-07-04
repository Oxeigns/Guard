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

def register(app: Client) -> None:

    async def require_admin_reply(message: Message, action: str) -> int | None:
        if not await is_admin(app, message):
            await message.reply_text("🚫 Only admins can do this.", parse_mode=ParseMode.HTML)
            return None
        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.reply_text(f"📌 Reply to a user to {action}.", parse_mode=ParseMode.HTML)
            return None
        return message.reply_to_message.from_user.id

    @app.on_message(filters.command("approve") & filters.group)
    @catch_errors
    async def approve_cmd(client: Client, message: Message):
        user_id = await require_admin_reply(message, "approve")
        if user_id is None: return
        await approve_user(message.chat.id, user_id)
        await message.reply_text(f"✅ Approved user <code>{user_id}</code>", parse_mode=ParseMode.HTML)

    @app.on_message(filters.command("unapprove") & filters.group)
    @catch_errors
    async def unapprove_cmd(client: Client, message: Message):
        user_id = await require_admin_reply(message, "unapprove")
        if user_id is None: return
        await unapprove_user(message.chat.id, user_id)
        await message.reply_text(f"❌ Unapproved user <code>{user_id}</code>", parse_mode=ParseMode.HTML)

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
        if not user or user.is_bot:
            return
        if await is_admin(client, message, user.id):
            return
        if not await get_approval_mode(message.chat.id):
            return
        if await is_approved(message.chat.id, user.id):
            return
        try:
            logger.info("Deleting message from unapproved user %s in chat %s", user.id, message.chat.id)
            await message.delete()
        except Exception as e:
            logger.warning("Failed to delete unapproved message: %s", e)
