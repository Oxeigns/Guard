from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from oxeign.utils.filters import admin_filter
from oxeign.swagger.settings import get_settings, set_mode, set_limit
from oxeign.swagger.biomode import is_biomode
from pyrogram.enums import ParseMode

VALID_MODES = {"off", "split", "telegraph"}

async def set_longmode(client: Client, message):
    if len(message.command) < 2:
        return await message.reply("❌ <b>Usage:</b> /setlongmode <off|split|telegraph>", parse_mode=ParseMode.HTML)
    mode = message.command[1].lower()
    if mode not in VALID_MODES:
        return await message.reply("❌ <b>Invalid mode</b>", parse_mode=ParseMode.HTML)
    await set_mode(message.chat.id, mode)
    await message.reply(f"✅ <b>Long mode set to {mode}</b>", parse_mode=ParseMode.HTML)

async def set_longlimit(client: Client, message):
    if len(message.command) < 2:
        return await message.reply("❌ <b>Usage:</b> /setlonglimit <number>", parse_mode=ParseMode.HTML)
    try:
        limit = int(message.command[1])
    except ValueError:
        return await message.reply("❌ <b>Limit must be a number</b>", parse_mode=ParseMode.HTML)
    await set_limit(message.chat.id, limit)
    await message.reply(f"✅ <b>Long limit set to {limit}</b>", parse_mode=ParseMode.HTML)

async def get_config(client: Client, message):
    settings = await get_settings(message.chat.id)
    biomode = await is_biomode(message.chat.id)
    text = (
        f"<b>Long mode:</b> {settings.get('mode')}\n"
        f"<b>Long limit:</b> {settings.get('limit')}\n"
        f"<b>Bio link mode:</b> {'on' if biomode else 'off'}"
    )
    await message.reply(text, parse_mode=ParseMode.HTML)


def register(app: Client):
    app.add_handler(
        MessageHandler(set_longmode, filters.command("setlongmode") & admin_filter)
    )
    app.add_handler(
        MessageHandler(set_longlimit, filters.command(["setlonglimit", "setlimit"]) & admin_filter)
    )
    app.add_handler(MessageHandler(get_config, filters.command("getconfig") & admin_filter))
