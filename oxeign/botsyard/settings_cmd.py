from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode

from oxeign.swagger.settings import get_settings, set_mode, set_limit
from oxeign.swagger.autodelete import get_autodelete, set_autodelete
from oxeign.swagger.biomode import is_biomode, set_biomode
from oxeign.utils.filters import admin_filter
from oxeign.utils.logger import log_to_channel


async def settings_cmd(client: Client, message):
    settings = await get_settings(message.chat.id)
    autodel = await get_autodelete(message.chat.id)
    biomode = await is_biomode(message.chat.id)

    text = (
        "<b>⚙️ Chat Settings</b>\n\n"
        f"<b>Long Mode:</b> {settings.get('mode')}\n"
        f"<b>Long Limit:</b> {settings.get('limit')}\n"
        f"<b>Bio Links:</b> {'on' if biomode else 'off'}\n"
        f"<b>Auto Delete:</b> {autodel}s"
    )

    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Set Long Mode", callback_data="set_longmode"),
             InlineKeyboardButton("Set Long Limit", callback_data="set_longlimit")],
            [InlineKeyboardButton("Toggle BioLink", callback_data="toggle_biolink"),
             InlineKeyboardButton("Set AutoDelete", callback_data="set_autodelete")],
            [InlineKeyboardButton("❌ Close", callback_data="close")],
        ]
    )
    await message.reply(text, reply_markup=buttons, parse_mode=ParseMode.HTML)


async def set_longmode_cb(client: Client, callback_query):
    await callback_query.answer()
    await callback_query.message.edit(
        "Send new mode: <code>off</code>, <code>split</code> or <code>telegraph</code>",
        parse_mode=ParseMode.HTML,
    )
    app = client
    app.add_handler(MessageHandler(longmode_receive, filters.private & filters.text), group=1)

async def longmode_receive(client: Client, message):
    mode = message.text.lower()
    if mode not in {"off", "split", "telegraph"}:
        return await message.reply("❌ Invalid mode")
    await set_mode(message.chat.id, mode)
    await message.reply(f"✅ Long mode set to {mode}", parse_mode=ParseMode.HTML)
    await log_to_channel(client, f"Long mode set to {mode} in {message.chat.id}")
    client.remove_handler(longmode_receive, group=1)

async def set_longlimit_cb(client: Client, callback_query):
    await callback_query.answer()
    await callback_query.message.edit(
        "Send new long limit (number)", parse_mode=ParseMode.HTML
    )
    client.add_handler(MessageHandler(longlimit_receive, filters.private & filters.text), group=2)

async def longlimit_receive(client: Client, message):
    try:
        limit = int(message.text)
    except ValueError:
        return await message.reply("❌ Must be a number")
    await set_limit(message.chat.id, limit)
    await message.reply(f"✅ Long limit set to {limit}", parse_mode=ParseMode.HTML)
    await log_to_channel(client, f"Long limit set to {limit} in {message.chat.id}")
    client.remove_handler(longlimit_receive, group=2)

async def toggle_biolink_cb(client: Client, callback_query):
    await callback_query.answer()
    enabled = not await is_biomode(callback_query.message.chat.id)
    await set_biomode(callback_query.message.chat.id, enabled)
    await callback_query.message.edit(
        f"✅ Bio link mode {'enabled' if enabled else 'disabled'}",
        parse_mode=ParseMode.HTML,
    )
    await log_to_channel(client, f"Bio mode set to {enabled} in {callback_query.message.chat.id}")

async def set_autodelete_cb(client: Client, callback_query):
    await callback_query.answer()
    await callback_query.message.edit(
        "Send auto delete seconds (0 to disable)", parse_mode=ParseMode.HTML
    )
    client.add_handler(MessageHandler(autodel_receive, filters.private & filters.text), group=3)

async def autodel_receive(client: Client, message):
    try:
        seconds = int(message.text)
    except ValueError:
        return await message.reply("❌ Must be a number")
    await set_autodelete(message.chat.id, seconds)
    await message.reply(f"✅ Auto delete set to {seconds}s", parse_mode=ParseMode.HTML)
    await log_to_channel(client, f"Auto delete set to {seconds}s in {message.chat.id}")
    client.remove_handler(autodel_receive, group=3)


def register(app: Client):
    app.add_handler(MessageHandler(settings_cmd, filters.command("settings") & admin_filter))
    app.add_handler(CallbackQueryHandler(set_longmode_cb, filters.regex("^set_longmode$")))
    app.add_handler(CallbackQueryHandler(set_longlimit_cb, filters.regex("^set_longlimit$")))
    app.add_handler(CallbackQueryHandler(toggle_biolink_cb, filters.regex("^toggle_biolink$")))
    app.add_handler(CallbackQueryHandler(set_autodelete_cb, filters.regex("^set_autodelete$")))
