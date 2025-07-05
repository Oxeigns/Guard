from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from .panels import send_start


def register(app: Client) -> None:
    @app.on_message(filters.command(["start", "help", "menu", "panel"]))
    async def send_panel(client: Client, message: Message):
        await send_start(client, message)

    @app.on_message(filters.command("id"))
    async def id_cmd(client: Client, message: Message) -> None:
        target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
        if message.chat.type in {"group", "supergroup", "channel"}:
            text = f"<b>Chat ID:</b> <code>{message.chat.id}</code>"
            if target:
                text += f"\n<b>User ID:</b> <code>{target.id}</code>"
        else:
            text = f"<b>Your ID:</b> <code>{target.id}</code>"
        await message.reply_text(text, parse_mode=ParseMode.HTML)
