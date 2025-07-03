"""Auto-delete messages after a delay."""

from pyrogram import Client, filters
from pyrogram.types import Message

from utils.storage import set_autodelete, get_autodelete
from utils.perms import is_admin


def register(app: Client):
    @app.on_message(filters.command("setautodelete") & filters.group)
    async def set_autodel(client: Client, message: Message):
        if not await is_admin(client, message):
            return
        try:
            seconds = int(message.command[1])
        except (IndexError, ValueError):
            await message.reply_text("Usage: /setautodelete <seconds>")
            return
        await set_autodelete(message.chat.id, seconds)
        if seconds > 0:
            await message.reply_text(
                f"🕒 Auto-delete set to {seconds} seconds.", parse_mode="Markdown"
            )
        else:
            await message.reply_text("❌ Auto-delete disabled.")

    @app.on_message(filters.group)
    async def autodelete_handler(client: Client, message: Message):
        if message.service:
            return
        if await is_admin(client, message, message.from_user.id):
            return
        delay = await get_autodelete(message.chat.id)
        if delay > 0:
            await message.delete(delay)
