from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from telegraph import upload_file
import tempfile

from utils.filters import admin_filter

MAX_TELEGRAPH_LEN = 4000

async def echo(client: Client, message):
    text = message.text or message.caption
    if not text:
        return
    if len(text) <= MAX_TELEGRAPH_LEN:
        await message.reply(text)
    else:
        with tempfile.NamedTemporaryFile('w+', delete=False) as f:
            f.write(text)
            f.flush()
            link = upload_file(f.name)[0]
        await message.reply(
            f"Message too long. Uploaded to https://telegra.ph{link}"
        )


def register(app: Client):
    app.add_handler(filters.command('echo') & admin_filter, echo)
