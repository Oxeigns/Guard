import logging
from pyrogram import Client, filters
from pyrogram.types import Message, ChatMemberUpdated
from config import LOG_GROUP_ID
from handlers.panels import send_control_panel
from utils.db import (
    add_user, add_group, remove_group,
    add_broadcast_user, add_broadcast_group,
    remove_broadcast_group,
)

logger = logging.getLogger(__name__)


def register(app: Client) -> None:
    print("✅ Registered: logging.py")

    # Log private /start usage
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
            f"🔹 Bot started by: {user.first_name or 'Unknown'} "
            f"(@{user.username or 'None'}) | ID: <code>{user.id}</code>"
        )
        try:
            await client.send_message(LOG_GROUP_ID, log_text)
        except Exception as exc:
            logger.warning("Failed to log /start: %s", exc)

    # Log when bot is added or removed from a group
    @app.on_chat_member_updated(group=-2)
    async def log_updates(client: Client, update: ChatMemberUpdated):
        chat = update.chat
        is_self = update.new_chat_member.user.is_self

        if is_self and update.old_chat_member.status in {"kicked", "left"}:
            # Bot added to a group
            try:
                await add_group(chat.id)
                await add_broadcast_group(chat.id)
            except Exception as exc:
                logger.warning("Failed to store group: %s", exc)

            inviter = update.from_user
            try:
                member_count = await client.get_chat_members_count(chat.id)
            except Exception:
                member_count = "unknown"

            name = inviter.first_name if inviter else "Unknown"
            username = f"@{inviter.username}" if inviter and inviter.username else "None"

            text = (
                f"🆕 <b>Added to group:</b> <b>{chat.title}</b>\n"
                f"<b>ID:</b> <code>{chat.id}</code>\n"
                f"<b>Members:</b> {member_count}\n"
                f"<b>By:</b> {name} ({username})"
            )

            try:
                await client.send_message(LOG_GROUP_ID, text)
            except Exception as exc:
                logger.warning("Failed to log group join: %s", exc)

            # Attempt to show the control panel
            try:
                from types import SimpleNamespace
                dummy_msg = SimpleNamespace(chat=chat, from_user=inviter)
                await send_control_panel(client, dummy_msg)
            except Exception as exc:
                logger.warning("Failed to send control panel: %s", exc)

        elif update.old_chat_member.user.is_self and update.new_chat_member.status in {"kicked", "left"}:
            # Bot removed from group
            try:
                await remove_group(chat.id)
                await remove_broadcast_group(chat.id)
            except Exception as exc:
                logger.warning("Failed to remove group: %s", exc)

            text = (
                f"❌ <b>Removed from group:</b> <b>{chat.title}</b>\n"
                f"<b>ID:</b> <code>{chat.id}</code>"
            )
            try:
                await client.send_message(LOG_GROUP_ID, text)
            except Exception as exc:
                logger.warning("Failed to log group removal: %s", exc)
