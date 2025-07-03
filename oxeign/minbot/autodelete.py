import asyncio
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from oxeign.swagger.autodelete import get_autodelete, set_autodelete
from oxeign.utils.perms import is_admin


async def delete_later(message: Message, delay: int):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception:
        pass


async def auto_delete_handler(client: Client, message: Message):
    if message.chat.type not in ("supergroup", "group"):
        return
    if message.from_user and message.from_user.is_self:
        return
    delay = await get_autodelete(message.chat.id)
    if delay > 0:
        asyncio.create_task(delete_later(message, delay))


async def set_autodel_cmd(client: Client, message: Message) -> None:
    """Set auto-delete delay in seconds via command."""
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].isdigit():
        await message.reply("Usage: /autodelete <seconds>")
        return
    seconds = int(parts[1])
    await set_autodelete(message.chat.id, seconds)
    await message.reply(f"Auto delete delay set to {seconds} seconds.")


def register(app: Client):
    app.add_handler(
        MessageHandler(auto_delete_handler, filters.group & ~filters.service),
        group=1,
    )
    app.add_handler(
        MessageHandler(set_autodel_cmd, filters.command("autodelete") & filters.group)
    )
