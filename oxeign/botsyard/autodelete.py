from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from oxeign.utils.filters import admin_filter
from oxeign.swagger.autodelete import set_autodelete, get_autodelete
from oxeign.utils.perms import is_admin
from oxeign.utils.logger import log_to_channel
import asyncio
async def set_autodelete_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: /setautodelete <seconds>")
    try:
        seconds = int(message.command[1])
    except ValueError:
        return await message.reply("❌ Seconds must be a number")
    await set_autodelete(message.chat.id, seconds)
    await message.reply("✅ Auto delete updated")
    await log_to_channel(client, f"Auto delete set to {seconds}s in {message.chat.id}")


async def auto_delete_handler(client: Client, message: Message):
    if not message.from_user or await is_admin(client, message.chat.id, message.from_user.id):
        return
    seconds = await get_autodelete(message.chat.id)
    if seconds > 0:
        await asyncio.sleep(seconds)
        try:
            await message.delete()
        except Exception:
            pass


def register(app: Client):
    app.add_handler(MessageHandler(set_autodelete_cmd, filters.command("setautodelete") & admin_filter))
    app.add_handler(MessageHandler(auto_delete_handler, filters.group & ~filters.service))

