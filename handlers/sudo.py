from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from utils.filters import admin_filter
from database.sudo import add_sudo, remove_sudo
from utils.logger import log_to_channel
from utils.perms import is_sudo


async def add_sudo_cmd(client: Client, message):
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply("Reply or provide a user id")
    user_id = (
        int(message.command[1]) if len(message.command) > 1 else message.reply_to_message.from_user.id
    )
    await add_sudo(user_id)
    await message.reply("User added as sudo")
    await log_to_channel(client, f"Added sudo {user_id}")


async def remove_sudo_cmd(client: Client, message):
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply("Reply or provide a user id")
    user_id = (
        int(message.command[1]) if len(message.command) > 1 else message.reply_to_message.from_user.id
    )
    if not await is_sudo(user_id):
        return await message.reply("User is not sudo")
    await remove_sudo(user_id)
    await message.reply("User removed from sudo")
    await log_to_channel(client, f"Removed sudo {user_id}")


def register(app: Client):
    app.add_handler(MessageHandler(add_sudo_cmd, filters.command("addsudo") & admin_filter))
    app.add_handler(MessageHandler(remove_sudo_cmd, filters.command("removesudo") & admin_filter))
