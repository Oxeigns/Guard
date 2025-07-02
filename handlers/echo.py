from pyrogram import Client, filters
from telegraph import upload_file
import tempfile

from utils.filters import admin_filter
from database.settings import get_settings

MAX_TELEGRAPH_LEN = 4000

async def echo(client: Client, message):
    text = message.text or message.caption
    if not text:
        return
    settings = await get_settings(message.chat.id)
    mode = settings.get("mode", "telegraph")
    limit = settings.get("limit", MAX_TELEGRAPH_LEN)

    if len(text) <= limit or mode == "off":
        await message.reply(text)
    else:
        if mode == "split":
            for i in range(0, len(text), limit):
                await message.reply(text[i : i + limit])
        else:
            with tempfile.NamedTemporaryFile("w+", delete=False) as f:
                f.write(text)
                f.flush()
                link = upload_file(f.name)[0]
            await message.reply(
                f"Message too long. Uploaded to https://telegra.ph{link}"
            )


def register(app: Client):
    app.add_handler(filters.command('echo') & admin_filter, echo)
