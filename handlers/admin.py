from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import ParseMode

from utils.errors import catch_errors
from utils.perms import is_admin
from utils.db import log_action


def init_admin(app: Client) -> None:
    async def _do_action(message: Message, action: str):
        if not await is_admin(app, message):
            await message.reply_text("Admins only", parse_mode=ParseMode.HTML)
            return
        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.reply_text("Reply to a user", parse_mode=ParseMode.HTML)
            return
        user = message.reply_to_message.from_user
        if action == "ban":
            await app.ban_chat_member(message.chat.id, user.id)
        elif action == "kick":
            await app.ban_chat_member(message.chat.id, user.id)
            await app.unban_chat_member(message.chat.id, user.id)
        elif action == "mute":
            await app.restrict_chat_member(message.chat.id, user.id, ChatPermissions())
        await message.reply_text(f"{action.title()} successful")
        await log_action(message.chat.id, user.id, action)

    @app.on_message(filters.command("ban") & filters.group)
    @catch_errors
    async def ban(_, message: Message):
        await _do_action(message, "ban")

    @app.on_message(filters.command("kick") & filters.group)
    @catch_errors
    async def kick(_, message: Message):
        await _do_action(message, "kick")

    @app.on_message(filters.command("mute") & filters.group)
    @catch_errors
    async def mute(_, message: Message):
        await _do_action(message, "mute")
