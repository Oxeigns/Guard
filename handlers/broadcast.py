from pyrogram import Client, filters
from utils.filters import admin_filter


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


def register(app: Client):
    app.add_handler(filters.command("broadcast") & admin_filter, broadcast)
