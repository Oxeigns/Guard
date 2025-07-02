from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.enums import ParseMode
from oxeign.utils.perms import get_role
from oxeign.utils.cleaner import auto_delete
from oxeign.swagger.groups import get_groups


async def status_cmd(client: Client, message):
    groups = await get_groups()
    role = await get_role(client, None, message.from_user.id)
    text = (
        f"<b>Bot Status</b>\n"
        f"Chats served: <code>{len(groups)}</code>\n"
        f"Your role: <b>{role}</b>"
    )
    reply = await message.reply(text, parse_mode=ParseMode.HTML)
    if message.chat.type != "private":
        client.loop.create_task(auto_delete(client, message, reply))


def register(app: Client):
    app.add_handler(MessageHandler(status_cmd, filters.command("status")))
