from pyrogram import Client, filters
from pyrogram.types import Message
from .panels import send_start


def register(app: Client) -> None:
    @app.on_message(filters.command(["start", "help", "menu", "panel"]))
    async def send_panel(client: Client, message: Message):
        await send_start(client, message)
