"""Permission helpers."""

from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus

async def is_admin(client: Client, message: Message, user_id: int | None = None) -> bool:
    user_id = user_id or message.from_user.id
    member = await client.get_chat_member(message.chat.id, user_id)
    return member.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}


async def is_member_of(client: Client, chat_id: int, user_id: int) -> bool:
    """Return True if the user is a member of the given chat."""
    try:
        member = await client.get_chat_member(chat_id, user_id)
    except Exception:
        return False
    return member.status not in {ChatMemberStatus.KICKED, ChatMemberStatus.LEFT}
