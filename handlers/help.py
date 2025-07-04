from pyrogram import Client, filters
from pyrogram.types import Message

HELP_TEXT = """Available commands:\n/start - welcome message\n/help - this help"""


def init_help(app: Client) -> None:
    @app.on_message(filters.command("help"))
    async def help_handler(client: Client, message: Message) -> None:
        await message.reply_text(HELP_TEXT)
