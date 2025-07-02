from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from utils.filters import admin_filter
from utils.perms import is_admin
from database.warns import add_warn, clear_warns
from utils.logger import log_to_channel


async def mute(client: Client, message):
    if not message.reply_to_message:
        return await message.reply("Reply to a user to mute")
    user_id = message.reply_to_message.from_user.id
    if await is_admin(client, message.chat.id, user_id):
        return await message.reply("Cannot mute an admin")
    await client.restrict_chat_member(message.chat.id, user_id, ChatPermissions())
    await message.reply("User muted")
    await log_to_channel(client, f"Muted {user_id} in {message.chat.id}")

async def unmute(client: Client, message):
    if not message.reply_to_message:
        return await message.reply("Reply to a user to unmute")
    user_id = message.reply_to_message.from_user.id
    await client.unban_chat_member(message.chat.id, user_id, only_if_banned=False)
    await message.reply("User unmuted")
    await log_to_channel(client, f"Unmuted {user_id} in {message.chat.id}")

async def ban(client: Client, message):
    if not message.reply_to_message:
        return await message.reply("Reply to a user to ban")
    user_id = message.reply_to_message.from_user.id
    if await is_admin(client, message.chat.id, user_id):
        return await message.reply("Cannot ban an admin")
    await client.ban_chat_member(message.chat.id, user_id)
    await message.reply("User banned")
    await log_to_channel(client, f"Banned {user_id} in {message.chat.id}")

async def unban(client: Client, message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply("Usage: reply or /unban user_id")
    user_id = int(message.command[1]) if len(message.command) > 1 else message.reply_to_message.from_user.id
    await client.unban_chat_member(message.chat.id, user_id)
    await message.reply("User unbanned")
    await log_to_channel(client, f"Unbanned {user_id} in {message.chat.id}")

async def kick(client: Client, message):
    if not message.reply_to_message:
        return await message.reply("Reply to a user to kick")
    user_id = message.reply_to_message.from_user.id
    if await is_admin(client, message.chat.id, user_id):
        return await message.reply("Cannot kick an admin")
    await client.ban_chat_member(message.chat.id, user_id)
    await client.unban_chat_member(message.chat.id, user_id)
    await message.reply("User kicked")
    await log_to_channel(client, f"Kicked {user_id} in {message.chat.id}")


async def warn(client: Client, message):
    if not message.reply_to_message:
        return await message.reply("Reply to a user to warn")
    user_id = message.reply_to_message.from_user.id
    if await is_admin(client, message.chat.id, user_id):
        return await message.reply("Cannot warn an admin")
    count = await add_warn(message.chat.id, user_id)
    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Clear Warns", callback_data=f"clearwarn:{user_id}")]]
    )
    await message.reply(f"User warned. Total warns: {count}", reply_markup=buttons)
    await log_to_channel(client, f"Warned {user_id} ({count}) in {message.chat.id}")


async def clear_warn_callback(client: Client, callback_query):
    data = callback_query.data.split(":")
    user_id = int(data[1])
    await clear_warns(callback_query.message.chat.id, user_id)
    await callback_query.answer("Warns cleared", show_alert=True)
    await callback_query.message.edit("Warns cleared")
    await log_to_channel(client, f"Cleared warns for {user_id} in {callback_query.message.chat.id}")


def register(app: Client):
    app.add_handler(MessageHandler(mute, filters.command("mute") & admin_filter))
    app.add_handler(MessageHandler(unmute, filters.command("unmute") & admin_filter))
    app.add_handler(MessageHandler(ban, filters.command("ban") & admin_filter))
    app.add_handler(MessageHandler(unban, filters.command("unban") & admin_filter))
    app.add_handler(MessageHandler(kick, filters.command("kick") & admin_filter))
    app.add_handler(MessageHandler(warn, filters.command("warn") & admin_filter))
    app.add_handler(CallbackQueryHandler(clear_warn_callback, filters.regex("^clearwarn:")))
