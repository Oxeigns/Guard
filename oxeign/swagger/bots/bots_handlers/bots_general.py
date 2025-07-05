import logging
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message
from .bots_commands import COMMANDS
from utils.errors import catch_errors

logger = logging.getLogger(__name__)


def register(app: Client) -> None:
    @app.on_message(filters.command("commands") & (filters.private | filters.group))
    @catch_errors
    async def commands_cmd(client: Client, message: Message) -> None:
        """Display the full command list as plain text."""
        rows = [f"{cmd} - {desc}" for cmd, desc in COMMANDS]
        help_text = "<b>📚 Commands</b>\n\n" + "\n".join(rows)
        logger.info("[COMMANDS] sent to %s", message.chat.id)

        await message.reply_text(
            help_text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
