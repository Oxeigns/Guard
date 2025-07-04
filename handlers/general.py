import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.errors import catch_errors
from panel import send_panel

logger = logging.getLogger(__name__)


def register(app: Client) -> None:
    @app.on_message(filters.command(["start", "help", "menu"]))
    @catch_errors
    async def show_panel(client: Client, message: Message) -> None:
        await send_panel(client, message)
