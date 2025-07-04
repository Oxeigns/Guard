from time import perf_counter
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message
from utils.errors import catch_errors


def register(app: Client) -> None:
    @app.on_message(filters.command("ping"))
    @catch_errors
    async def ping_cmd(client: Client, message: Message) -> None:
        """
        Responds with bot latency in ms.
        """
        start = perf_counter()
        msg = await message.reply_text("📡 Pinging...")
        latency = round((perf_counter() - start) * 1000, 2)
        await msg.edit_text(
            f"🎉 Pong! <code>{latency}ms</code>",
            parse_mode=ParseMode.HTML
        )
