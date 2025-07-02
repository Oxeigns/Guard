from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from oxeign.config import OWNER_ID, SUDO_USERS
from oxeign.swagger.sudo import get_sudos

async def is_sudo(user_id: int) -> bool:
    sudos = SUDO_USERS + await get_sudos()
    return user_id in sudos or user_id == OWNER_ID

async def is_admin(client: Client, chat_id: int, user_id: int) -> bool:
    if await is_sudo(user_id):
        return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
    except Exception:
        return False
    return member.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR)
