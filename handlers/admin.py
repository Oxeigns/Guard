from pyrogram import Client, filters
from pyrogram.types import ChatPermissions
from utils.filters import admin_filter


async def mute(client: Client, message):
    if not message.reply_to_message:
        return await message.reply("Reply to a user to mute")
    user_id = message.reply_to_message.from_user.id
    await client.restrict_chat_member(
        message.chat.id, user_id, permissions=ChatPermissions()
    )
    await message.reply("User muted")

async def unmute(client: Client, message):
    if not message.reply_to_message:
        return await message.reply("Reply to a user to unmute")
    user_id = message.reply_to_message.from_user.id
    await client.unban_chat_member(message.chat.id, user_id, only_if_banned=False)
    await message.reply("User unmuted")

async def ban(client: Client, message):
    if not message.reply_to_message:
        return await message.reply("Reply to a user to ban")
    user_id = message.reply_to_message.from_user.id
    await client.ban_chat_member(message.chat.id, user_id)
    await message.reply("User banned")

async def unban(client: Client, message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply("Usage: reply or /unban user_id")
    user_id = int(message.command[1]) if len(message.command) > 1 else message.reply_to_message.from_user.id
    await client.unban_chat_member(message.chat.id, user_id)
    await message.reply("User unbanned")

async def kick(client: Client, message):
    if not message.reply_to_message:
        return await message.reply("Reply to a user to kick")
    user_id = message.reply_to_message.from_user.id
    await client.ban_chat_member(message.chat.id, user_id)
    await client.unban_chat_member(message.chat.id, user_id)
    await message.reply("User kicked")


async def warn(client: Client, message):
    if not message.reply_to_message:
        return await message.reply("Reply to a user to warn")
    await message.reply("User warned")


def register(app: Client):
    app.add_handler(filters.command("mute") & admin_filter, mute)
    app.add_handler(filters.command("unmute") & admin_filter, unmute)
    app.add_handler(filters.command("ban") & admin_filter, ban)
    app.add_handler(filters.command("unban") & admin_filter, unban)
    app.add_handler(filters.command("kick") & admin_filter, kick)
    app.add_handler(filters.command("warn") & admin_filter, warn)
