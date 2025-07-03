"""Auto-delete messages after a delay."""

import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

from utils.db import set_autodelete, get_autodelete
from utils.perms import is_admin
from utils.errors import catch_errors

logger = logging.getLogger(__name__)


def register(app: Client) -> None:
    @app.on_message(filters.command(["setautodelete", "autodelete"]) & filters.group)
    @catch_errors
    async def set_autodel(client: Client, message: Message):
        logger.info(
            "%s command in %s by %s",
            message.command[0],
            message.chat.id,
            message.from_user.id if message.from_user else None,
        )
        if not await is_admin(client, message):
            await message.reply_text("❌ You must be an admin to use this command.")
            return
        if len(message.command) == 1 and message.command[0] == "autodelete":
            delay = await get_autodelete(message.chat.id)
            await message.reply_text(f"Current auto-delete setting: {delay} seconds")
            return
        try:
            seconds = int(message.command[1])
        except (IndexError, ValueError):
            await message.reply_text("Usage: /autodelete <seconds>")
            return
        await set_autodelete(message.chat.id, seconds)
        if seconds > 0:
            await message.reply_text(f"🕒 Auto-delete set to {seconds} seconds.")
        else:
            await message.reply_text("❌ Auto-delete disabled.")

    @app.on_message(filters.group)
    @catch_errors
    async def autodelete_handler(client: Client, message: Message):
        logger.debug("autodelete check in %s", message.chat.id)
        if not (message.text or message.caption):
            return
        if message.from_user is None:
            return
        if await is_admin(client, message, message.from_user.id):
            return
        delay = await get_autodelete(message.chat.id)
        if delay > 0:
            await asyncio.sleep(delay)
            await message.delete()
