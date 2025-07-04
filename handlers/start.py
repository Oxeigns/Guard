from pyrogram import Client, filters
from pyrogram.types import Message


def init_start(app: Client) -> None:
    @app.on_message(filters.command("start"))
    async def start_handler(client: Client, message: Message) -> None:
        await message.reply_text("Hello! I'm alive.")
