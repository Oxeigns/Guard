"""Auto delete handler."""
import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message

from utils.storage import Storage
from utils.perms import is_user_admin
from handlers.logs import log

storage = Storage()


async def schedule_deletion(client: Client, message: Message, delay: int) -> None:
    """Delete a message after ``delay`` seconds."""
    await asyncio.sleep(delay)
    await client.delete_messages(message.chat.id, message.id, revoke=True)
    await log(client, f"🧹 Deleted a message in `{message.chat.id}` after {delay}s")


@Client.on_message(filters.command("setautodelete") & filters.group)
async def set_auto_delete(client: Client, message: Message) -> None:
    """Set auto delete delay."""
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if not await is_user_admin(member):
        return
    if len(message.command) < 2:
        await message.reply_text("Usage: /setautodelete <seconds|12h|24h|off>")
        return
    value = message.command[1].lower()
    delay: int = 0
    if value == "off":
        delay = 0
    elif value.endswith("h") and value[:-1].isdigit():
        hours = int(value[:-1])
        delay = hours * 3600
    elif value.isdigit():
        delay = int(value)
    await storage.update_settings(message.chat.id, autodelete=delay)
    text = "AutoDelete disabled" if delay == 0 else f"AutoDelete set to {delay}s"
    await message.reply_text(text)


@Client.on_message(filters.group & ~filters.service)
async def apply_autodelete(client: Client, message: Message) -> None:
    """Apply auto delete to incoming messages."""
    settings = await storage.get_settings(message.chat.id)
    delay = settings.get("autodelete", 0)
    if not delay:
        return
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if await is_user_admin(member):
        return
    asyncio.create_task(schedule_deletion(client, message, delay))

