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
from utils.db import get_users, get_groups

logger = logging.getLogger(__name__)


def register(app: Client) -> None:
    @app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
    async def broadcast_cmd(client: Client, message: Message):
        if len(message.command) < 2 or message.command[1] not in {"users", "groups"}:
            await message.reply_text("Usage: /broadcast users|groups <text> or reply")
            return
        target = message.command[1]
        if message.reply_to_message:
            payload_msg = message.reply_to_message
            payload_text = None
        else:
            if len(message.command) < 3:
                await message.reply_text("Provide text or reply to a message")
                return
            payload_text = message.text.split(None, 2)[2]
            payload_msg = None
        ids = await (get_users() if target == "users" else get_groups())
        sent = 0
        failed = 0
        for cid in ids:
            try:
                if payload_msg:
                    await payload_msg.copy(cid)
                else:
                    await client.send_message(cid, payload_text, parse_mode=ParseMode.HTML)
                sent += 1
            except FloodWait as e:
                await asyncio.sleep(e.value)
                try:
                    if payload_msg:
                        await payload_msg.copy(cid)
                    else:
                        await client.send_message(cid, payload_text, parse_mode=ParseMode.HTML)
                    sent += 1
                except (ChatWriteForbidden, UserKicked, PeerIdInvalid, UserIsBlocked, Exception):
                    failed += 1
            except (ChatWriteForbidden, UserKicked, PeerIdInvalid, UserIsBlocked, Exception):
                failed += 1
            await asyncio.sleep(0.1)
        await message.reply_text(f"✅ Done. Sent: {sent}, Failed: {failed}")
