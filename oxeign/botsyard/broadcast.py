from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from oxeign.utils.perms import is_sudo
from oxeign.utils.logger import log_to_channel
from oxeign.swagger.groups import get_groups
from pyrogram.enums import ParseMode
from datetime import datetime
import uuid

_cache = {}


async def broadcast_preview(client: Client, message):
    if not await is_sudo(message.from_user.id):
        return
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply(
            "❌ <b>Usage:</b> /broadcast <text> or reply to a message",
            parse_mode=ParseMode.HTML,
        )
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else message.reply_to_message.text
    key = str(uuid.uuid4())
    _cache[key] = text
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Confirm", callback_data=f"bc:{key}"),
                InlineKeyboardButton("❌ Cancel", callback_data=f"bccancel:{key}"),
            ]
        ]
    )
    await message.reply(f"<b>Broadcast Preview:</b>\n\n{text}", reply_markup=buttons, parse_mode=ParseMode.HTML)


async def broadcast_send(client: Client, callback_query):
    key = callback_query.data.split(":", 1)[1]
    text = _cache.pop(key, None)
    if not text:
        await callback_query.answer("Expired", show_alert=True)
        return
    sent = 0
    for chat_id in await get_groups():
        try:
            await client.send_message(chat_id, text)
            sent += 1
        except Exception:
            continue
    await callback_query.message.edit(f"✅ <b>Broadcast sent to {sent} chats</b>", parse_mode=ParseMode.HTML)
    ts = datetime.utcnow().isoformat()
    await log_to_channel(client, f"Broadcast by {callback_query.from_user.id} to {sent} chats at {ts}")


async def broadcast_cancel(client: Client, callback_query):
    key = callback_query.data.split(":", 1)[1]
    _cache.pop(key, None)
    await callback_query.message.edit("❌ Broadcast cancelled")


def register(app: Client):
    app.add_handler(MessageHandler(broadcast_preview, filters.command("broadcast")))
    app.add_handler(CallbackQueryHandler(broadcast_send, filters.regex("^bc:")))
    app.add_handler(CallbackQueryHandler(broadcast_cancel, filters.regex("^bccancel:")))
