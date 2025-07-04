"""Delete messages with links and provide admin toggle."""

import logging
import re
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from utils.db import (
    get_link_filter,
    toggle_link_filter,
    set_link_filter,
    is_approved,
)
from utils.perms import is_admin
from utils.errors import catch_errors

logger = logging.getLogger(__name__)

LINK_RE = re.compile(r"(https?://|t\.me/|telegram\.me/)", re.IGNORECASE)


def register(app: Client) -> None:
    @app.on_message(filters.command("linkfilter") & filters.group)
    @catch_errors
    async def linkfilter_cmd(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text(
                "🔒 Only admins can toggle link filtering.",
                parse_mode=ParseMode.HTML,
            )
            return

        if len(message.command) == 1:
            state = await toggle_link_filter(message.chat.id)
        else:
            arg = message.command[1].lower()
            if arg in {"on", "enable", "true"}:
                await set_link_filter(message.chat.id, True)
                state = True
            elif arg in {"off", "disable", "false"}:
                await set_link_filter(message.chat.id, False)
                state = False
            else:
                await message.reply_text(
                    "Usage: /linkfilter [on|off]",
                    parse_mode=ParseMode.HTML,
                )
                return

        await message.reply_text(
            f"🔗 Link filter is now <b>{'ENABLED ✅' if state else 'DISABLED ❌'}</b>",
            parse_mode=ParseMode.HTML,
        )

    @app.on_message(filters.group & (filters.text | filters.caption))
    @catch_errors
    async def enforce_linkfilter(client: Client, message: Message):
        if not await get_link_filter(message.chat.id):
            return
        if not message.from_user or message.from_user.is_bot:
            return
        if await is_admin(client, message, message.from_user.id):
            return
        if await is_approved(message.chat.id, message.from_user.id):
            return

        text = message.text or message.caption or ""
        if LINK_RE.search(text):
            try:
                await message.delete()
                logger.info(
                    "Deleted link message from %s in chat %s",
                    message.from_user.id,
                    message.chat.id,
                )
            except Exception as e:
                logger.warning("Failed to delete link message: %s", e)

