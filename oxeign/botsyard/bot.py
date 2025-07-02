from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from oxeign.config import START_IMAGE

async def start(client: Client, message):
    text = "I am alive!"
    await message.reply_photo(START_IMAGE, caption=text) if START_IMAGE else await message.reply(text)

async def help_cmd(client: Client, message):
    help_text = "Available commands: /approve, /disapprove, /setlongmode, /setlonglimit, /biolink, /broadcast, /mute, /unmute, /ban, /unban, /kick, /warn, /addsudo, /removesudo"
    await message.reply(help_text)


def register(app: Client):
    app.add_handler(MessageHandler(start, filters.command("start")))
    app.add_handler(MessageHandler(help_cmd, filters.command("help")))
