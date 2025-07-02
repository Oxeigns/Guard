from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.enums import ParseMode
from oxeign.utils.filters import admin_filter
from oxeign.utils.perms import is_admin, is_sudo
from oxeign.utils.cleaner import auto_delete
from oxeign.swagger.warns import add_warn, clear_warns
from oxeign.utils.logger import log_to_channel
from oxeign.swagger.groups import get_groups


async def mute(client: Client, message):
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user to mute")
    user_id = message.reply_to_message.from_user.id
    if await is_admin(client, message.chat.id, user_id):
        return await message.reply("❌ Cannot mute an admin")
    await client.restrict_chat_member(message.chat.id, user_id, ChatPermissions())
    reply = await message.reply("✅ User muted")
    await log_to_channel(client, f"Muted {user_id} in {message.chat.id}")
    client.loop.create_task(auto_delete(client, message, reply))

async def unmute(client: Client, message):
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user to unmute")
    user_id = message.reply_to_message.from_user.id
    await client.unban_chat_member(message.chat.id, user_id, only_if_banned=False)
    reply = await message.reply("✅ User unmuted")
    await log_to_channel(client, f"Unmuted {user_id} in {message.chat.id}")
    client.loop.create_task(auto_delete(client, message, reply))

async def ban(client: Client, message):
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user to ban")
    user_id = message.reply_to_message.from_user.id
    if await is_admin(client, message.chat.id, user_id):
        return await message.reply("❌ Cannot ban an admin")
    await client.ban_chat_member(message.chat.id, user_id)
    reply = await message.reply("✅ User banned")
    await log_to_channel(client, f"Banned {user_id} in {message.chat.id}")
    client.loop.create_task(auto_delete(client, message, reply))

async def unban(client: Client, message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply("❌ Usage: reply or /unban user_id")
    user_id = int(message.command[1]) if len(message.command) > 1 else message.reply_to_message.from_user.id
    await client.unban_chat_member(message.chat.id, user_id)
    reply = await message.reply("✅ User unbanned")
    await log_to_channel(client, f"Unbanned {user_id} in {message.chat.id}")
    client.loop.create_task(auto_delete(client, message, reply))

async def gban(client: Client, message):
    if not await is_sudo(message.from_user.id):
        return
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user to gban")
    user_id = message.reply_to_message.from_user.id
    count = 0
    for chat_id in await get_groups():
        try:
            await client.ban_chat_member(chat_id, user_id)
            count += 1
        except Exception:
            continue
    reply = await message.reply(f"✅ Globally banned in {count} chats")
    await log_to_channel(client, f"Gban {user_id} by {message.from_user.id} ({count})")
    client.loop.create_task(auto_delete(client, message, reply))

async def gunban(client: Client, message):
    if not await is_sudo(message.from_user.id):
        return
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user to gunban")
    user_id = message.reply_to_message.from_user.id
    count = 0
    for chat_id in await get_groups():
        try:
            await client.unban_chat_member(chat_id, user_id)
            count += 1
        except Exception:
            continue
    reply = await message.reply(f"✅ Globally unbanned in {count} chats")
    await log_to_channel(client, f"Gunban {user_id} by {message.from_user.id} ({count})")
    client.loop.create_task(auto_delete(client, message, reply))

async def gmute(client: Client, message):
    if not await is_sudo(message.from_user.id):
        return
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user to gmute")
    user_id = message.reply_to_message.from_user.id
    count = 0
    for chat_id in await get_groups():
        try:
            await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
            count += 1
        except Exception:
            continue
    reply = await message.reply(f"✅ Globally muted in {count} chats")
    await log_to_channel(client, f"Gmute {user_id} by {message.from_user.id} ({count})")
    client.loop.create_task(auto_delete(client, message, reply))

async def gunmute(client: Client, message):
    if not await is_sudo(message.from_user.id):
        return
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user to gunmute")
    user_id = message.reply_to_message.from_user.id
    count = 0
    for chat_id in await get_groups():
        try:
            await client.unban_chat_member(chat_id, user_id, only_if_banned=False)
            count += 1
        except Exception:
            continue
    reply = await message.reply(f"✅ Globally unmuted in {count} chats")
    await log_to_channel(client, f"Gunmute {user_id} by {message.from_user.id} ({count})")
    client.loop.create_task(auto_delete(client, message, reply))

async def kick(client: Client, message):
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user to kick")
    user_id = message.reply_to_message.from_user.id
    if await is_admin(client, message.chat.id, user_id):
        return await message.reply("❌ Cannot kick an admin")
    await client.ban_chat_member(message.chat.id, user_id)
    await client.unban_chat_member(message.chat.id, user_id)
    reply = await message.reply("✅ User kicked")
    await log_to_channel(client, f"Kicked {user_id} in {message.chat.id}")
    client.loop.create_task(auto_delete(client, message, reply))


async def warn(client: Client, message):
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user to warn")
    user_id = message.reply_to_message.from_user.id
    if await is_admin(client, message.chat.id, user_id):
        return await message.reply("❌ Cannot warn an admin")
    count = await add_warn(message.chat.id, user_id)
    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Clear Warns", callback_data=f"clearwarn:{user_id}")]]
    )
    reply = await message.reply(f"⚠️ User warned. Total warns: {count}", reply_markup=buttons)
    await log_to_channel(client, f"Warned {user_id} ({count}) in {message.chat.id}")
    client.loop.create_task(auto_delete(client, message, reply))


async def clear_warn_callback(client: Client, callback_query):
    data = callback_query.data.split(":")
    user_id = int(data[1])
    await clear_warns(callback_query.message.chat.id, user_id)
    await callback_query.answer("Warns cleared", show_alert=True)
    await callback_query.message.edit("Warns cleared")
    await log_to_channel(client, f"Cleared warns for {user_id} in {callback_query.message.chat.id}")
    client.loop.create_task(auto_delete(client, callback_query.message))


def register(app: Client):
    app.add_handler(MessageHandler(mute, filters.command("mute") & admin_filter))
    app.add_handler(MessageHandler(unmute, filters.command("unmute") & admin_filter))
    app.add_handler(MessageHandler(ban, filters.command("ban") & admin_filter))
    app.add_handler(MessageHandler(unban, filters.command("unban") & admin_filter))
    app.add_handler(MessageHandler(kick, filters.command("kick") & admin_filter))
    app.add_handler(MessageHandler(warn, filters.command("warn") & admin_filter))
    app.add_handler(CallbackQueryHandler(clear_warn_callback, filters.regex("^clearwarn:")))
    app.add_handler(MessageHandler(gban, filters.command("gban")))
    app.add_handler(MessageHandler(gunban, filters.command("gunban")))
    app.add_handler(MessageHandler(gmute, filters.command("gmute")))
    app.add_handler(MessageHandler(gunmute, filters.command("gunmute")))
