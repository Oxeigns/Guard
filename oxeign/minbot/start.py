from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode

from oxeign.utils.logger import log_to_channel
from oxeign.config import BOT_NAME


async def start_cmd(client: Client, message):
    text = (
        f"**Welcome to {BOT_NAME}!**\n\n"
        "Use /panel in groups to configure settings."
    )
    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Support", url="https://t.me/Botsyard")]]
    )
    await message.reply(text, reply_markup=buttons, parse_mode=ParseMode.MARKDOWN)
    if message.chat.type == "private":
        await log_to_channel(
            client,
            f"#START\nUser: {message.from_user.mention} ({message.from_user.id})",
        )


def register(app: Client):
    app.add_handler(MessageHandler(start_cmd, filters.command("start")))
