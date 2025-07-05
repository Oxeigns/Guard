"""Permission utilities."""

import logging
from pyrogram import Client
from pyrogram.types import Message, ChatMember
from pyrogram.enums import ChatType, ChatMemberStatus

logger = logging.getLogger(__name__)

async def is_admin(client: Client, message: Message, user_id: int = None) -> bool:
    """
    Checks whether the given user (or message sender) is an admin in the chat.
    Supports groups and supergroups.
    """
    # Private chats have no admin concept
    if message.chat.type == ChatType.PRIVATE:
        return False

    try:
        chat_id = message.chat.id
        user_id = user_id or message.from_user.id
        member: ChatMember = await client.get_chat_member(chat_id, user_id)
        return member.status in {
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER,
        }
    except Exception as exc:  # noqa: BLE001
        logger.debug(
            "Admin check failed for %s in %s: %s",
            user_id or (message.from_user.id if message.from_user else 0),
            message.chat.id,
            exc,
        )
        return False
