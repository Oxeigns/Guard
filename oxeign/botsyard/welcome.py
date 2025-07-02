from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.handlers import MessageHandler
from oxeign.swagger.welcome import set_welcome, get_welcome
from oxeign.utils.filters import admin_filter
from oxeign.utils.logger import log_to_channel


async def set_welcome_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: /setwelcome <text>")
    text = message.text.split(None, 1)[1]
    await set_welcome(message.chat.id, text)
    await message.reply("✅ Welcome message saved")
    await log_to_channel(client, f"Set welcome in {message.chat.id}")


async def new_member(client: Client, message: Message):
    welcome = await get_welcome(message.chat.id)
    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🛠 Commands", callback_data="help"), InlineKeyboardButton("📣 Support", url="https://t.me/Botsyard")]]
    )
    for user in message.new_chat_members:
        text = welcome.format(mention=user.mention)
        await message.reply(text, reply_markup=buttons if user.is_self else None)
        if user.is_self:
            await log_to_channel(client, f"Bot added to {message.chat.id}")


def register(app: Client):
    app.add_handler(MessageHandler(set_welcome_cmd, filters.command("setwelcome") & admin_filter))
    app.add_handler(MessageHandler(new_member, filters.group & filters.new_chat_members))
