import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.errors import (
    FloodWait,
    ChatWriteForbidden,
    PeerIdInvalid,
    UserIsBlocked,
    UserKicked,
)
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from config import OWNER_ID
from utils.db import get_broadcast_groups

logger = logging.getLogger(__name__)


def register(app: Client) -> None:
    @app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
    async def broadcast_cmd(client: Client, message: Message) -> None:
        """Broadcast a message to all known groups."""
        logger.debug("[BROADCAST] broadcast initiated by %s", message.from_user.id)
        if message.reply_to_message:
            payload_msg = message.reply_to_message
            text = None
        else:
            if len(message.command) < 2:
                await message.reply_text("Usage: /broadcast <text> or reply to a message")
                return
            text = message.text.split(None, 1)[1]
            payload_msg = None

        ids = await get_broadcast_groups()
        sent = 0
        failed = 0
        for cid in ids:
            try:
                if payload_msg:
                    await payload_msg.copy(cid)
                else:
                    await client.send_message(cid, text, parse_mode=ParseMode.HTML)
                sent += 1
            except FloodWait as e:
                await asyncio.sleep(e.value)
                try:
                    if payload_msg:
                        await payload_msg.copy(cid)
                    else:
                        await client.send_message(cid, text, parse_mode=ParseMode.HTML)
                    sent += 1
                except (ChatWriteForbidden, UserKicked, PeerIdInvalid, UserIsBlocked, Exception):
                    failed += 1
            except (ChatWriteForbidden, UserKicked, PeerIdInvalid, UserIsBlocked, Exception):
                failed += 1
            await asyncio.sleep(0.1)
        await message.reply_text(f"✅ Done. Sent: {sent}, Failed: {failed}")
