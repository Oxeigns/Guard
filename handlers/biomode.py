from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from utils.filters import admin_filter
from database.biomode import set_biomode
from utils.logger import log_to_channel


async def toggle_biolink(client: Client, message):
    if len(message.command) < 2:
        return await message.reply("Usage: /biolink on|off")
    mode = message.command[1].lower()
    enabled = mode == "on"
    await set_biomode(message.chat.id, enabled)
    await message.reply(f"Bio link mode {'enabled' if enabled else 'disabled'}")
    await log_to_channel(client, f"Bio mode set to {enabled} in {message.chat.id}")


def register(app: Client):
    app.add_handler(MessageHandler(toggle_biolink, filters.command("biolink") & admin_filter))
