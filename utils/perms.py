from pyrogram.enums import ChatMemberStatus


async def is_admin(client, message, user_id: int | None = None) -> bool:
    """
    Check if the user is an admin or owner in the chat.

    Args:
        client: Pyrogram Client
        message: Pyrogram Message object
        user_id (optional): User ID to check. If None, checks the message sender.

    Returns:
        bool: True if user is admin or owner, else False
    """
    if not user_id:
        if not message.from_user:
            return False
        user_id = message.from_user.id

    try:
        member = await client.get_chat_member(message.chat.id, user_id)
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except Exception:
        return False
