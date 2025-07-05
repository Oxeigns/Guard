import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from .panels import send_start

logger = logging.getLogger(__name__)


def register(app: Client) -> None:
    @app.on_message(filters.command(["start", "help", "menu", "panel"]))
    async def send_panel(client: Client, message: Message):
        logger.debug("[GENERAL] panel command in chat %s", message.chat.id)
        await send_start(client, message)

    @app.on_message(filters.command("id"))
    async def id_cmd(client: Client, message: Message) -> None:
        """Return chat and/or user IDs."""
        from pyrogram.enums import ChatType
        logger.debug("[GENERAL] id command in chat %s", message.chat.id)

        target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
        if message.chat.type in {ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL}:
            text = f"<b>Chat ID:</b> <code>{message.chat.id}</code>"
            if target:
                text += f"\n<b>User ID:</b> <code>{target.id}</code>"
        else:
            text = f"<b>Your ID:</b> <code>{target.id}</code>"
        await message.reply_text(text, parse_mode=ParseMode.HTML)

    @app.on_message(filters.command("ping"))
    async def ping_cmd(client: Client, message: Message) -> None:
        """Simple health check command."""
        logger.debug("[GENERAL] ping command in chat %s", message.chat.id)
        await message.reply_text("🏓 Pong!")
