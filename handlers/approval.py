"""User approval management."""

import logging
from pyrogram import Client, filters
from pyrogram.types import Message

from utils.db import (
    approve_user,
    unapprove_user,
    get_approved,
    is_approved,
    get_approval_mode,
    toggle_approval_mode,
    set_approval_mode,
)
from utils.perms import is_admin
from utils.errors import catch_errors

logger = logging.getLogger(__name__)


def register(app: Client) -> None:
    @app.on_message(filters.command("approve") & filters.group)
    @catch_errors
    async def approve_cmd(client: Client, message: Message):
        logger.info("approve command in %s by %s", message.chat.id, message.from_user.id if message.from_user else None)
        if not await is_admin(client, message):
            await message.reply_text("❌ You must be an admin to use this command.")
            return
        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.reply_text("Reply to a user to approve.")
            return
        user_id = message.reply_to_message.from_user.id
        await approve_user(message.chat.id, user_id)
        await message.reply_text(f"✅ Approved <code>{user_id}</code>")

    @app.on_message(filters.command("unapprove") & filters.group)
    @catch_errors
    async def unapprove_cmd(client: Client, message: Message):
        logger.info("unapprove command in %s by %s", message.chat.id, message.from_user.id if message.from_user else None)
        if not await is_admin(client, message):
            await message.reply_text("❌ You must be an admin to use this command.")
            return
        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.reply_text("Reply to a user to unapprove.")
            return
        user_id = message.reply_to_message.from_user.id
        await unapprove_user(message.chat.id, user_id)
        await message.reply_text(f"❌ Unapproved <code>{user_id}</code>")

    @app.on_message(filters.command("viewapproved") & filters.group)
    @catch_errors
    async def view_approved(client: Client, message: Message):
        logger.info("viewapproved command in %s by %s", message.chat.id, message.from_user.id if message.from_user else None)
        if not await is_admin(client, message):
            await message.reply_text("❌ You must be an admin to use this command.")
            return
        users = await get_approved(message.chat.id)
        if not users:
            await message.reply_text("📭 No approved users.")
            return
        text = "<b>📋 Approved Users:</b>\n" + "\n".join(f"<code>{u}</code>" for u in users)
        await message.reply_text(text)

    @app.on_message(filters.command("approval") & filters.group)
    @catch_errors
    async def approval_mode_cmd(client: Client, message: Message):
        logger.info("approval toggle in %s", message.chat.id)
        if not await is_admin(client, message):
            await message.reply_text("❌ You must be an admin to use this command.")
            return
        if len(message.command) == 1:
            enabled = await toggle_approval_mode(message.chat.id)
        else:
            arg = message.command[1].lower()
            if arg in {"on", "enable", "true"}:
                await set_approval_mode(message.chat.id, True)
                enabled = True
            elif arg in {"off", "disable", "false"}:
                await set_approval_mode(message.chat.id, False)
                enabled = False
            else:
                await message.reply_text("Usage: /approval [on|off]")
                return
        await message.reply_text(f"Approval mode {'ON' if enabled else 'OFF'}")

    @app.on_message(filters.group, group=10)
    @catch_errors
    async def enforce_approval(client: Client, message: Message):
        if message.from_user is None or message.from_user.is_bot:
            return
        if await is_admin(client, message, message.from_user.id):
            return
        if not await get_approval_mode(message.chat.id):
            return
        if await is_approved(message.chat.id, message.from_user.id):
            return
        try:
            await message.delete()
        except Exception:
            pass
