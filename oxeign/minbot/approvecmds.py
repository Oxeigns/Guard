from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from pyrogram.enums import ParseMode

from oxeign.utils.perms import is_admin
from oxeign.swagger.approvals import add_approval, remove_approval


async def approve_cmd(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return
    if not message.reply_to_message:
        await message.reply("Reply to a user's message to approve them.")
        return
    target_id = message.reply_to_message.from_user.id
    await add_approval(message.chat.id, target_id)
    await message.reply(
        f"Approved [user](tg://user?id={target_id})",
        parse_mode=ParseMode.MARKDOWN,
    )


async def unapprove_cmd(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return
    if not message.reply_to_message:
        await message.reply("Reply to a user's message to unapprove them.")
        return
    target_id = message.reply_to_message.from_user.id
    await remove_approval(message.chat.id, target_id)
    await message.reply(
        f"Unapproved [user](tg://user?id={target_id})",
        parse_mode=ParseMode.MARKDOWN,
    )


def register(app: Client):
    app.add_handler(MessageHandler(approve_cmd, filters.command("approve") & filters.group))
    app.add_handler(MessageHandler(unapprove_cmd, filters.command("unapprove") & filters.group))
