from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from oxeign.utils.filters import admin_filter
from oxeign.utils.logger import log_to_channel


async def broadcast(client: Client, message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply("Usage: /broadcast <text> or reply to a message")
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else message.reply_to_message.text
    sent = 0
    async for dialog in client.get_dialogs():
        try:
            await client.send_message(dialog.chat.id, text)
            sent += 1
        except Exception:
            continue
    await message.reply(f"Broadcast sent to {sent} chats")
    await log_to_channel(client, f"Broadcast by {message.from_user.id} to {sent} chats")


def register(app: Client):
    app.add_handler(MessageHandler(broadcast, filters.command("broadcast") & admin_filter))
