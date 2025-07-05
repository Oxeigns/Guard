import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, ChatMemberUpdated
from config import OWNER_ID, LOG_GROUP_ID
from utils.errors import catch_errors
from utils.db import (
    add_broadcast_user,
    add_broadcast_group,
    remove_broadcast_group,
    get_broadcast_users,
    get_broadcast_groups,
)

logger = logging.getLogger(__name__)

LOG_PREFIX = "ᯓ𓆰 ❛-OxygenBot ᭄ꪾ"


def register(app: Client) -> None:
    @app.on_message(filters.command("start") & filters.private, group=-2)
    @catch_errors
    async def log_start(client: Client, message: Message) -> None:
        user = message.from_user
        if not user:
            return
        await add_broadcast_user(user.id)
        username = f"@{user.username}" if user.username else "N/A"
        full_name = user.first_name
        if user.last_name:
            full_name += f" {user.last_name}"
        text = (
            f"{LOG_PREFIX} Started by: `{full_name}`,"
            f" ID: `{user.id}`,"
            f" Username: `{username}`"
        )
        try:
            await client.send_message(LOG_GROUP_ID, text, parse_mode=ParseMode.HTML)
        except Exception as exc:
            logger.warning("Failed to log start: %s", exc)

    @app.on_chat_member_updated(group=-2)
    @catch_errors
    async def log_bot_events(client: Client, update: ChatMemberUpdated) -> None:
        chat = update.chat
        # Bot added to a group
        if update.new_chat_member.user.is_self and update.old_chat_member.status in {"kicked", "left"}:
            await add_broadcast_group(chat.id)
            adder = update.from_user
            adder_name = (
                f"@{adder.username}" if adder and adder.username else (adder.mention if adder else "Unknown")
            )
            try:
                count = await client.get_chat_members_count(chat.id)
                member_info = f", Members: {count}"
            except Exception:
                member_info = ""
            text = (
                f"{LOG_PREFIX} Added to Group: `{chat.title}`,"
                f" ID: `{chat.id}`,"
                f" by: `{adder_name}`{member_info}"
            )
            try:
                await client.send_message(LOG_GROUP_ID, text, parse_mode=ParseMode.HTML)
            except Exception as exc:
                logger.warning("Failed to log group add: %s", exc)
        # Bot removed from a group
        elif update.old_chat_member.user.is_self and update.new_chat_member.status in {"kicked", "left"}:
            await remove_broadcast_group(chat.id)
            text = (
                f"{LOG_PREFIX} Removed from Group: `{chat.title}`,"
                f" ID: `{chat.id}`"
            )
            try:
                await client.send_message(LOG_GROUP_ID, text, parse_mode=ParseMode.HTML)
            except Exception as exc:
                logger.warning("Failed to log group leave: %s", exc)

    @app.on_message(filters.new_chat_members, group=-2)
    @catch_errors
    async def on_added_via_message(client: Client, message: Message) -> None:
        for user in message.new_chat_members:
            if user.is_self:
                await add_broadcast_group(message.chat.id)
                adder = message.from_user
                adder_name = (
                    f"@{adder.username}" if adder and adder.username else (adder.mention if adder else "Unknown")
                )
                try:
                    count = await client.get_chat_members_count(message.chat.id)
                    member_info = f", Members: {count}"
                except Exception:
                    member_info = ""
                text = (
                    f"{LOG_PREFIX} Added to Group: `{message.chat.title}`,"
                    f" ID: `{message.chat.id}`,"
                    f" by: `{adder_name}`{member_info}"
                )
                try:
                    await client.send_message(LOG_GROUP_ID, text, parse_mode=ParseMode.HTML)
                except Exception as exc:
                    logger.warning("Failed to log group add: %s", exc)

    @app.on_message(filters.command("broadcast") & filters.user(OWNER_ID), group=1)
    @catch_errors
    async def broadcast_cmd(client: Client, message: Message) -> None:
        if len(message.command) < 2 or message.command[1] not in {"users", "groups"}:
            await message.reply_text("Usage: /broadcast users|groups <text> or reply")
            return
        target = message.command[1]
        if message.reply_to_message:
            payload_msg = message.reply_to_message
            payload_text = None
        else:
            if len(message.command) < 3:
                await message.reply_text("Provide text or reply to a message to broadcast")
                return
            payload_msg = None
            payload_text = message.text.split(None, 2)[2]
        ids = await (get_broadcast_users() if target == "users" else get_broadcast_groups())
        success = 0
        fail = 0
        for cid in ids:
            try:
                if payload_msg:
                    await payload_msg.copy(cid)
                else:
                    await client.send_message(cid, payload_text, parse_mode=ParseMode.HTML)
                success += 1
            except Exception:
                fail += 1
            await asyncio.sleep(0.1)
        await message.reply_text(f"Broadcast complete. Success: {success}, Failed: {fail}")
