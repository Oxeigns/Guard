from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from oxeign.config import START_IMAGE

async def start(client: Client, message):
    text = "I am alive!"
    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Updates", url="https://t.me/botsyard"), InlineKeyboardButton("Support", url="https://t.me/botsyard")]]
    )
    if START_IMAGE:
        await message.reply_photo(START_IMAGE, caption=text, reply_markup=buttons)
    else:
        await message.reply(text, reply_markup=buttons)

async def help_cmd(client: Client, message):
    help_text = (
        "Available commands: /approve, /disapprove, /setlongmode, /setlonglimit, "
        "/biolink, /broadcast, /mute, /unmute, /ban, /unban, /kick, /warn, /addsudo, /rmsudo"
    )
    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Updates", url="https://t.me/botsyard"), InlineKeyboardButton("Support", url="https://t.me/botsyard")]]
    )
    await message.reply(help_text, reply_markup=buttons)


def register(app: Client):
    app.add_handler(MessageHandler(start, filters.command("start")))
    app.add_handler(MessageHandler(help_cmd, filters.command("help")))
