import logging
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message
from .commands import COMMANDS
from utils.errors import catch_errors
from .bots_settings import send_start, send_control_panel

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

    @app.on_message(filters.command(["help", "menu", "menuu", "settings"]) & (filters.private | filters.group))
    @catch_errors
    async def panel_cmd(client: Client, message: Message) -> None:
        """
        Handle /help, /menu or /settings commands in both private and group chats.
        Opens the control panel with current settings.
        """
        source = "private" if message.chat.type == "private" else f"group {message.chat.id}"
        logger.info(f"[HELP/MENU] triggered from {source}")
        if message.chat.type == "private":
            await send_start(client, message)
        else:
            await send_control_panel(client, message)

    @app.on_message(filters.command("commands") & (filters.private | filters.group))
    @catch_errors
    async def commands_cmd(client: Client, message: Message) -> None:
        """Display the full commands list without using buttons."""
        rows = [f"{cmd} - {desc}" for cmd, desc in COMMANDS]
        help_text = "<b>\ud83d\udcda Commands</b>\n\n" + "\n".join(rows)
        logger.info("[COMMANDS] sent to %s", message.chat.id)
        await message.reply_text(help_text, parse_mode=ParseMode.HTML)
