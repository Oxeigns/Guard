from pyrogram import Client
from pyrogram.handlers import ChatMemberUpdatedHandler
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import ChatMemberUpdated
from oxeign.swagger.groups import add_group, remove_group
from oxeign.utils.logger import get_logger

logger = get_logger(__name__)

async def my_chat_member_update(client: Client, update: ChatMemberUpdated):
    if not update.new_chat_member.user.is_self:
        return
    status = update.new_chat_member.status
    if status in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR):
        await add_group(update.chat.id)
        logger.info(f"Joined chat {update.chat.id}")
    elif status in (ChatMemberStatus.KICKED, ChatMemberStatus.LEFT):
        await remove_group(update.chat.id)
        logger.info(f"Left chat {update.chat.id}")


def register(app: Client):
    app.add_handler(ChatMemberUpdatedHandler(my_chat_member_update))
