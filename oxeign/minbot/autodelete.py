import asyncio
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from oxeign.swagger.autodelete import get_autodelete


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


def register(app: Client):
    app.add_handler(MessageHandler(auto_delete_handler, filters.group & ~filters.service), group=1)
