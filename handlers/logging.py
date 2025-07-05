import logging
from pyrogram import Client, filters
from pyrogram.types import Message, ChatMemberUpdated
from config import LOG_GROUP_ID
from utils.db import add_user, add_group, remove_group

logger = logging.getLogger(__name__)


def register(app: Client) -> None:
    @app.on_message(filters.command("start") & filters.private, group=-2)
    async def log_start(client: Client, message: Message):
        user = message.from_user
        if not user:
            return
        await add_user(user.id)
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
            await add_group(chat.id)
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
        elif update.old_chat_member.user.is_self and update.new_chat_member.status in {"kicked", "left"}:
            await remove_group(chat.id)
            text = f"❌ Removed from group: {chat.title} | ID: {chat.id}"
            try:
                await client.send_message(LOG_GROUP_ID, text)
            except Exception as exc:
                logger.warning("Failed to log group remove: %s", exc)
