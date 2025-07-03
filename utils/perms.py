"""Permission helpers."""

from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus

async def is_admin(client: Client, message: Message, user_id: int | None = None) -> bool:
    user_id = user_id or message.from_user.id
    member = await client.get_chat_member(message.chat.id, user_id)
    return member.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}
