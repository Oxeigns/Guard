from pyrogram import Client
from pyrogram.handlers import ChatMemberUpdatedHandler
from pyrogram.types import ChatMemberUpdated
from pyrogram.enums import ChatMemberStatus

from oxeign.utils.logger import log_to_channel


async def track_updates(client: Client, update: ChatMemberUpdated):
    if not update.new_chat_member or not update.new_chat_member.user:
        return
    if not update.new_chat_member.user.is_self:
        return
    status = update.new_chat_member.status
    if status in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR):
        await log_to_channel(client, f"#ADDED\nChat: {update.chat.id}")
    elif status in (ChatMemberStatus.KICKED, ChatMemberStatus.LEFT):
        await log_to_channel(client, f"#REMOVED\nChat: {update.chat.id}")


def register(app: Client):
    app.add_handler(ChatMemberUpdatedHandler(track_updates))
