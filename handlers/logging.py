import logging
from pyrogram import Client, filters
from pyrogram.types import Message, ChatMemberUpdated
from config import LOG_GROUP_ID
from .panels import send_control_panel
from utils.db import (
    add_user,
    add_group,
    remove_group,
    add_broadcast_user,
    add_broadcast_group,
    remove_broadcast_group,
)

logger = logging.getLogger(__name__)


def register(app: Client) -> None:
    print("✅ Registered: logging.py")
    ...
    @app.on_message(filters.command("start") & filters.private, group=-2)
    async def log_start(client: Client, message: Message):
        user = message.from_user
        if not user:
            return
        try:
            await add_user(user.id)
            await add_broadcast_user(user.id)
        except Exception as exc:
            logger.warning("Failed to store user: %s", exc)
        log_text = (
            f"🔹 Bot started by: {user.first_name or 'Unknown'} (@{user.username or 'None'}) | ID: {user.id}"
        )
        try:
            await client.send_message(LOG_GROUP_ID, log_text)
        except Exception as exc:
            logger.warning("Failed to log start: %s", exc)

    @app.on_chat_member_updated(group=-2)
    async def log_updates(client: Client, update: ChatMemberUpdated):
        chat = update.chat
        if update.new_chat_member.user.is_self and update.old_chat_member.status in {"kicked", "left"}:
            try:
                await add_group(chat.id)
                await add_broadcast_group(chat.id)
            except Exception as exc:
                logger.warning("Failed to store group: %s", exc)
            inviter = update.from_user
            try:
                count = await client.get_chat_members_count(chat.id)
            except Exception:
                count = 0
            name = inviter.first_name if inviter else "Unknown"
            username = f"@{inviter.username}" if inviter and inviter.username else "None"
            text = f"🆕 Added to group: {chat.title} | ID: {chat.id} | Members: {count} | By: {name} ({username})"
            try:
                await client.send_message(LOG_GROUP_ID, text)
            except Exception as exc:
                logger.warning("Failed to log group add: %s", exc)
            # Show control panel in the new group
            try:
                from types import SimpleNamespace

                dummy = SimpleNamespace(chat=chat, from_user=inviter)
                await send_control_panel(client, dummy)
            except Exception as exc:
                logger.warning("Failed to send control panel: %s", exc)
        elif update.old_chat_member.user.is_self and update.new_chat_member.status in {"kicked", "left"}:
            try:
                await remove_group(chat.id)
                await remove_broadcast_group(chat.id)
            except Exception as exc:
                logger.warning("Failed to remove group: %s", exc)
            text = f"❌ Removed from group: {chat.title} | ID: {chat.id}"
            try:
                await client.send_message(LOG_GROUP_ID, text)
            except Exception as exc:
                logger.warning("Failed to log group remove: %s", exc)
