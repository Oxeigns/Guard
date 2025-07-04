import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.errors import catch_errors
from panel import send_start, send_control_panel

logger = logging.getLogger(__name__)


def register(app: Client) -> None:
    @app.on_message(filters.command("start"))
    @catch_errors
    async def start_cmd(client: Client, message: Message) -> None:
        await send_start(client, message)

    @app.on_message(filters.command(["help", "menu"]))
    @catch_errors
    async def panel_cmd(client: Client, message: Message) -> None:
        await send_control_panel(client, message)
