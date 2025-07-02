from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from oxeign.utils.filters import admin_filter
from oxeign.swagger.biomode import set_biomode
from oxeign.utils.logger import log_to_channel
from pyrogram.enums import ParseMode


async def toggle_biolink(client: Client, message):
    if len(message.command) < 2:
        return await message.reply("❌ <b>Usage:</b> /biolink on|off", parse_mode=ParseMode.HTML)
    mode = message.command[1].lower()
    enabled = mode == "on"
    await set_biomode(message.chat.id, enabled)
    await message.reply(f"✅ <b>Bio link mode {'enabled' if enabled else 'disabled'}</b>", parse_mode=ParseMode.HTML)
    await log_to_channel(client, f"Bio mode set to {enabled} in {message.chat.id}")


def register(app: Client):
    app.add_handler(MessageHandler(toggle_biolink, filters.command("biolink") & admin_filter))
