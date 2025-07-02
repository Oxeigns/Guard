from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.handlers import MessageHandler
from oxeign.swagger.welcome import set_welcome, get_welcome
from oxeign.utils.filters import admin_filter
from oxeign.utils.logger import log_to_channel
from pyrogram.enums import ParseMode
from datetime import datetime


async def set_welcome_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ <b>Usage:</b> /setwelcome <text>", parse_mode=ParseMode.HTML)
    text = message.text.split(None, 1)[1]
    await set_welcome(message.chat.id, text)
    await message.reply("✅ <b>Welcome message saved</b>", parse_mode=ParseMode.HTML)
    await log_to_channel(client, f"Set welcome in {message.chat.id}")


async def new_member(client: Client, message: Message):
    welcome = await get_welcome(message.chat.id)
    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🛠 Commands", callback_data="help"), InlineKeyboardButton("📣 Support", url="https://t.me/Botsyard")]]
    )
    for user in message.new_chat_members:
        text = welcome.format(mention=user.mention)
        await message.reply(text, reply_markup=buttons if user.is_self else None)
        ts = datetime.utcnow().isoformat()
        if user.is_self:
            await log_to_channel(client, f"Bot added to {message.chat.id}")
        else:
            log_text = (
                f"#JOIN\nName: {user.first_name} {user.last_name or ''}\nID: {user.id}\n"
                f"Username: @{user.username or 'N/A'}\nLink: {user.mention('link')}\n"
                f"Chat: {message.chat.id}\nTimestamp: {ts}"
            )
            await log_to_channel(client, log_text)


def register(app: Client):
    app.add_handler(MessageHandler(set_welcome_cmd, filters.command("setwelcome") & admin_filter))
    app.add_handler(MessageHandler(new_member, filters.group & filters.new_chat_members))
