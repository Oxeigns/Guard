from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from oxeign.utils.filters import admin_filter
from oxeign.utils.logger import log_to_channel


async def purge(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a message to start purging")

    chat_id = message.chat.id
    start_id = message.reply_to_message.id
    end_id = message.id
    ids = list(range(start_id, end_id))
    for msg_id in ids:
        try:
            await client.delete_messages(chat_id, msg_id)
        except Exception:
            pass
    await log_to_channel(client, f"Purged messages in {chat_id} from {start_id} to {end_id}")
    await message.reply("✅ Purge complete")


def register(app: Client):
    app.add_handler(MessageHandler(purge, filters.command("purge") & admin_filter))
