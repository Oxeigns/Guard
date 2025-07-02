from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode

from oxeign.swagger.settings import (
    get_settings,
    set_mode,
    set_limit,
    toggle_setting,
)
from oxeign.swagger.autodelete import get_autodelete, set_autodelete
from oxeign.swagger.biomode import is_biomode, set_biomode
from oxeign.utils.filters import admin_filter
from oxeign.utils.logger import log_to_channel


async def build_settings(client: Client, chat_id: int):
    settings = await get_settings(chat_id)
    autodel = await get_autodelete(chat_id)
    biomode = await is_biomode(chat_id)

    text = (
        "<b>⚙️ Chat Settings</b>\n\n"
        f"<b>Long Mode:</b> {settings.get('mode')}\n"
        f"<b>Long Limit:</b> {settings.get('limit')}\n"
        f"<b>Bio Links:</b> {'on' if biomode else 'off'}\n"
        f"<b>Auto Delete:</b> {autodel}s\n"
        f"<b>Anti-Spam:</b> {'on' if settings.get('anti_spam') else 'off'}\n"
        f"<b>Anti-Flood:</b> {'on' if settings.get('anti_flood') else 'off'}\n"
        f"<b>Captcha:</b> {'on' if settings.get('captcha') else 'off'}\n"
        f"<b>Tag All:</b> {'on' if settings.get('tag_all') else 'off'}\n"
        f"<b>Link Control:</b> {'on' if settings.get('link_control') else 'off'}\n"
        f"<b>Media Filter:</b> {'on' if settings.get('media_filter') else 'off'}\n"
        f"<b>Night Mode:</b> {'on' if settings.get('night_mode') else 'off'}"
    )

    rows = [
        [
            InlineKeyboardButton("Set Long Mode", callback_data="set_longmode"),
            InlineKeyboardButton("Set Long Limit", callback_data="set_longlimit"),
        ],
        [
            InlineKeyboardButton(
                "Toggle BioLink", callback_data="toggle_biolink"
            ),
            InlineKeyboardButton("Set AutoDelete", callback_data="set_autodelete"),
        ],
        [
            InlineKeyboardButton(
                f"Anti-Spam {'✅' if settings.get('anti_spam') else '❌'}",
                callback_data="toggle:anti_spam",
            ),
            InlineKeyboardButton(
                f"Anti-Flood {'✅' if settings.get('anti_flood') else '❌'}",
                callback_data="toggle:anti_flood",
            ),
        ],
        [
            InlineKeyboardButton(
                f"Captcha {'✅' if settings.get('captcha') else '❌'}",
                callback_data="toggle:captcha",
            ),
            InlineKeyboardButton(
                f"TagAll {'✅' if settings.get('tag_all') else '❌'}",
                callback_data="toggle:tag_all",
            ),
        ],
        [
            InlineKeyboardButton(
                f"LinkCtrl {'✅' if settings.get('link_control') else '❌'}",
                callback_data="toggle:link_control",
            ),
            InlineKeyboardButton(
                f"MediaFlt {'✅' if settings.get('media_filter') else '❌'}",
                callback_data="toggle:media_filter",
            ),
        ],
        [
            InlineKeyboardButton(
                f"NightMode {'✅' if settings.get('night_mode') else '❌'}",
                callback_data="toggle:night_mode",
            ),
        ],
        [InlineKeyboardButton("❌ Close", callback_data="close")],
    ]

    markup = InlineKeyboardMarkup(rows)
    return text, markup


async def settings_cmd(client: Client, message):
    text, markup = await build_settings(client, message.chat.id)
    await message.reply(text, reply_markup=markup, parse_mode=ParseMode.HTML)


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
    text, markup = await build_settings(client, callback_query.message.chat.id)
    await callback_query.message.edit(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await log_to_channel(client, f"Bio mode set to {enabled} in {callback_query.message.chat.id}")

async def set_autodelete_cb(client: Client, callback_query):
    await callback_query.answer()
    await callback_query.message.edit(
        "Send auto delete seconds (0 to disable)", parse_mode=ParseMode.HTML
    )
    client.add_handler(MessageHandler(autodel_receive, filters.private & filters.text), group=3)

async def toggle_setting_cb(client: Client, callback_query):
    await callback_query.answer()
    key = callback_query.data.split(":", 1)[1]
    state = await toggle_setting(callback_query.message.chat.id, key)
    text, markup = await build_settings(client, callback_query.message.chat.id)
    await callback_query.message.edit(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await log_to_channel(client, f"{key} set to {state} in {callback_query.message.chat.id}")

async def autodel_receive(client: Client, message):
    try:
        seconds = int(message.text)
    except ValueError:
        return await message.reply("❌ Must be a number")
    await set_autodelete(message.chat.id, seconds)
    await message.reply(f"✅ Auto delete set to {seconds}s", parse_mode=ParseMode.HTML)
    await log_to_channel(client, f"Auto delete set to {seconds}s in {message.chat.id}")
    text, markup = await build_settings(client, message.chat.id)
    await message.reply(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    client.remove_handler(autodel_receive, group=3)


def register(app: Client):
    app.add_handler(MessageHandler(settings_cmd, filters.command("settings") & admin_filter))
    app.add_handler(CallbackQueryHandler(set_longmode_cb, filters.regex("^set_longmode$")))
    app.add_handler(CallbackQueryHandler(set_longlimit_cb, filters.regex("^set_longlimit$")))
    app.add_handler(CallbackQueryHandler(toggle_biolink_cb, filters.regex("^toggle_biolink$")))
    app.add_handler(CallbackQueryHandler(set_autodelete_cb, filters.regex("^set_autodelete$")))
    app.add_handler(CallbackQueryHandler(toggle_setting_cb, filters.regex("^toggle:")))
