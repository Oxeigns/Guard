import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.errors import catch_errors
from panel import send_start, send_control_panel

logger = logging.getLogger(__name__)


def register(app: Client) -> None:
    @app.on_message(filters.command("start") & filters.private)
    @catch_errors
    async def start_cmd(client: Client, message: Message) -> None:
        """
        Handle /start command in private chats.
        Displays the welcome screen with start panel.
        """
        logger.info(f"[START] from user {message.from_user.id}")
        await send_start(client, message)

    @app.on_message(filters.command(["help", "menu"]) & (filters.private | filters.group))
    @catch_errors
    async def panel_cmd(client: Client, message: Message) -> None:
        """
        Handle /help or /menu command in both private and group chats.
        Opens control panel with current settings.
        """
        source = "private" if message.chat.type == "private" else f"group {message.chat.id}"
        logger.info(f"[HELP/MENU] triggered from {source}")
        await send_control_panel(client, message)
