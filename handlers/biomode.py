from pyrogram import Client, filters
from utils.filters import admin_filter
from database import biomode


async def toggle_biolink(client: Client, message):
    if len(message.command) < 2:
        return await message.reply("Usage: /biolink on|off")
    mode = message.command[1].lower()
    enabled = mode == 'on'
    biomode.update_one({"chat_id": message.chat.id}, {"$set": {"enabled": enabled}}, upsert=True)
    await message.reply(f"Bio link mode {'enabled' if enabled else 'disabled'}")


def register(app: Client):
    app.add_handler(filters.command("biolink") & admin_filter, toggle_biolink)
