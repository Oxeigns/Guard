"""User approval management."""

from pyrogram import Client, filters
from pyrogram.types import Message

from utils.storage import approve_user, unapprove_user, get_approved
from utils.perms import is_admin


def register(app: Client):
    @app.on_message(filters.command("approve") & filters.group)
    async def approve_cmd(client: Client, message: Message):
        if not await is_admin(client, message):
            return
        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.reply_text("Reply to a user to approve.")
            return
        user_id = message.reply_to_message.from_user.id
        await approve_user(message.chat.id, user_id)
        await message.reply_text(
            f"✅ Approved `{user_id}`", parse_mode="Markdown"
        )

    @app.on_message(filters.command("unapprove") & filters.group)
    async def unapprove_cmd(client: Client, message: Message):
        if not await is_admin(client, message):
            return
        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.reply_text("Reply to a user to unapprove.")
            return
        user_id = message.reply_to_message.from_user.id
        await unapprove_user(message.chat.id, user_id)
        await message.reply_text(
            f"❌ Unapproved `{user_id}`", parse_mode="Markdown"
        )

    @app.on_message(filters.command("viewapproved") & filters.group)
    async def view_approved(client: Client, message: Message):
        if not await is_admin(client, message):
            return
        users = await get_approved(message.chat.id)
        if not users:
            await message.reply_text("📭 No approved users.")
            return
        text = "**📋 Approved Users:**\n" + "\n".join(f"`{u}`" for u in users)
        await message.reply_text(text, parse_mode="Markdown")
