from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from oxeign.utils.perms import is_sudo
from oxeign.utils.logger import log_to_channel
from oxeign.swagger.groups import get_groups
from pyrogram.enums import ParseMode


async def broadcast(client: Client, message):
    if not await is_sudo(message.from_user.id):
        return
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply("❌ <b>Usage:</b> /broadcast <text> or reply to a message", parse_mode=ParseMode.HTML)
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else message.reply_to_message.text
    sent = 0
    for chat_id in await get_groups():
        try:
            await client.send_message(chat_id, text)
            sent += 1
        except Exception:
            continue
    await message.reply(f"✅ <b>Broadcast sent to {sent} chats</b>", parse_mode=ParseMode.HTML)
    await log_to_channel(client, f"Broadcast by {message.from_user.id} to {sent} chats")


def register(app: Client):
    app.add_handler(MessageHandler(broadcast, filters.command("broadcast")))
