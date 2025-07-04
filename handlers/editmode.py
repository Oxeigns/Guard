"""Delete edited messages after a delay when enabled."""

import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from utils.db import (
    toggle_edit_mode,
    set_edit_mode,
    get_edit_mode,
)
from utils.perms import is_admin
from utils.errors import catch_errors

logger = logging.getLogger(__name__)

DELAY_SECONDS = 900


def register(app: Client) -> None:
    @app.on_message(filters.command("editmode") & filters.group)
    @catch_errors
    async def editmode_cmd(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text(
                "🔒 Only admins can toggle edit mode.",
                parse_mode=ParseMode.HTML,
            )
            return

        if len(message.command) == 1:
            state = await toggle_edit_mode(message.chat.id)
        else:
            arg = message.command[1].lower()
            if arg in {"on", "enable", "true"}:
                await set_edit_mode(message.chat.id, True)
                state = True
            elif arg in {"off", "disable", "false"}:
                await set_edit_mode(message.chat.id, False)
                state = False
            else:
                await message.reply_text(
                    "Usage: /editmode [on|off]",
                    parse_mode=ParseMode.HTML,
                )
                return

        await message.reply_text(
            f"✏️ Edit mode is now <b>{'ENABLED ✅' if state else 'DISABLED ❌'}</b>",
            parse_mode=ParseMode.HTML,
        )

    @app.on_message(filters.edited & filters.group)
    @catch_errors
    async def delete_later(client: Client, message: Message):
        if not await get_edit_mode(message.chat.id):
            return
        if not message.from_user or message.from_user.is_bot:
            return
        await asyncio.sleep(DELAY_SECONDS)
        try:
            await message.delete()
            logger.info(
                "Deleted edited message from %s in chat %s",
                message.from_user.id,
                message.chat.id,
            )
        except Exception as e:
            logger.warning("Failed to delete edited message: %s", e)

