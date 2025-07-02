from pyrogram import filters
from utils.perms import is_admin


async def admin_filter_func(_, client, message):
    return await is_admin(client, message.chat.id, message.from_user.id)

admin_filter = filters.create(admin_filter_func)
