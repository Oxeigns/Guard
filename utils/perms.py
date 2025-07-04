"""Permission helpers."""

import logging
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus, ChatType

logger = logging.getLogger(__name__)

async def is_admin(client: Client, message: Message, user_id: int | None = None) -> bool:
    """Return ``True`` if the user is an admin of the chat."""
    if message.chat.type == ChatType.PRIVATE:
        return True

    user_id = user_id or message.from_user.id
    try:
        member = await client.get_chat_member(message.chat.id, user_id)
    except Exception as exc:
        logger.warning("get_chat_member failed: %s", exc)
        return False

    return member.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}


async def is_member_of(client: Client, chat_id: int, user_id: int) -> bool:
    """Return True if the user is a member of the given chat."""
    try:
        member = await client.get_chat_member(chat_id, user_id)
    except Exception as exc:
        logger.debug("get_chat_member(%s, %s) failed: %s", chat_id, user_id, exc)
        return False
    return member.status not in {ChatMemberStatus.KICKED, ChatMemberStatus.LEFT}
