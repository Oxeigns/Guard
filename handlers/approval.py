"""User approval management."""

import logging
from pyrogram import Client, filters
from pyrogram.types import Message

from utils.storage import approve_user, unapprove_user, get_approved
from utils.perms import is_admin
from utils.errors import catch_errors

logger = logging.getLogger(__name__)


def init(app: Client) -> None:
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
