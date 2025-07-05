from pyrogram import Client
from pyrogram.types import Message, ChatMember
from pyrogram.enums import ChatType

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
        return member.status in ("administrator", "creator")
    except Exception as e:
        # Fallback to False if any error occurs
        print(f"[is_admin] Error checking admin status: {e}")
        return False
