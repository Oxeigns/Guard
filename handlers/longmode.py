from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from utils.filters import admin_filter
from database.settings import set_mode, set_limit

VALID_MODES = {"off", "split", "telegraph"}

async def set_longmode(client: Client, message):
    if len(message.command) < 2:
        return await message.reply("Usage: /setlongmode <off|split|telegraph>")
    mode = message.command[1].lower()
    if mode not in VALID_MODES:
        return await message.reply("Invalid mode")
    await set_mode(message.chat.id, mode)
    await message.reply(f"Long mode set to {mode}")

async def set_longlimit(client: Client, message):
    if len(message.command) < 2:
        return await message.reply("Usage: /setlonglimit <number>")
    try:
        limit = int(message.command[1])
    except ValueError:
        return await message.reply("Limit must be a number")
    await set_limit(message.chat.id, limit)
    await message.reply(f"Long limit set to {limit}")


def register(app: Client):
    app.add_handler(MessageHandler(set_longmode, filters.command("setlongmode") & admin_filter))
    app.add_handler(MessageHandler(set_longlimit, filters.command("setlonglimit") & admin_filter))
