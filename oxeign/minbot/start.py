from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler


from oxeign.utils.logger import log_to_channel
from oxeign.config import BOT_NAME
from .panel import send_panel


async def start_cmd(client: Client, message):
    if message.chat.type == "private":
        await send_panel(client, message)
        await log_to_channel(
            client,
            f"#START\nUser: {message.from_user.mention} ({message.from_user.id})",
        )


def register(app: Client):
    app.add_handler(MessageHandler(start_cmd, filters.command("start")))

