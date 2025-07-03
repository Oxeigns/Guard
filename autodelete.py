from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from utils.storage import set_autodelete, get_autodelete
from utils.perms import is_admin

def register(app: Client):
    @app.on_message(filters.command("setautodelete") & filters.group)
    async def set_autodelete_cmd(client, message: Message):
        if not await is_admin(client, message):
            return
        try:
            seconds = int(message.command[1])
            await set_autodelete(message.chat.id, seconds)
            if seconds > 0:
                await message.reply_text(f"🕒 Auto-delete enabled: {seconds} seconds.")
            else:
                await message.reply_text("❌ Auto-delete disabled.")
        except (IndexError, ValueError):
            await message.reply_text("Usage: /setautodelete <seconds>")

    @app.on_message(filters.group)
    async def autodelete_handler(client, message: Message):
        if message.service or await is_admin(client, message, message.from_user.id):
            return
        delay = await get_autodelete(message.chat.id)
        if delay > 0:
            await message.delete(delay)
