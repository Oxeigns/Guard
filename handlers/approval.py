"""Approval command handlers."""

from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from utils.storage import Storage
from utils.perms import is_user_admin

storage = Storage()


@Client.on_message(filters.command("approve") & filters.group & filters.reply)
async def approve_user(client: Client, message: Message) -> None:
    """Approve a user by reply."""
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if not await is_user_admin(member):
        return
    user = message.reply_to_message.from_user
    await storage.approve_user(message.chat.id, user.id)
    await storage.reset_warnings(message.chat.id, user.id)
    await message.reply_text(f"✅ {user.mention} approved.")


@Client.on_message(filters.command("unapprove") & filters.group & filters.reply)
async def unapprove_user(client: Client, message: Message) -> None:
    """Unapprove a user by reply."""
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if not await is_user_admin(member):
        return
    user = message.reply_to_message.from_user
    await storage.unapprove_user(message.chat.id, user.id)
    await message.reply_text(f"❌ {user.mention} unapproved.")


@Client.on_message(filters.command("approved") & filters.group)
async def list_approved(client: Client, message: Message) -> None:
    """List all approved users in the chat."""
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if not await is_user_admin(member):
        return
    users = await storage.get_approved_users(message.chat.id)
    if not users:
        await message.reply_text("No approved users.")
        return
    mentions = []
    for uid in users:
        user = await client.get_users(uid)
        mentions.append(user.mention)
    await message.reply_text(
        "*Approved users:*\n" + "\n".join(mentions),
        parse_mode=ParseMode.MARKDOWN,
    )
