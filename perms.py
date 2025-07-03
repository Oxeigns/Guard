from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus

async def is_admin(client, message: Message, user_id: int = None):
    user_id = user_id or message.from_user.id
    member = await client.get_chat_member(message.chat.id, user_id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]

