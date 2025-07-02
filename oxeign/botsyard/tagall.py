from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.enums import ParseMode
from oxeign.utils.filters import admin_filter
from oxeign.utils.logger import log_to_channel
import asyncio


async def tagall(client: Client, message):
    if len(message.command) > 1:
        note = message.text.split(None, 1)[1]
    else:
        note = ""

    mentions = []
    async for member in client.get_chat_members(message.chat.id):
        if member.user.is_bot:
            continue
        mentions.append(member.user.mention)
        if len(mentions) == 5:
            text = f"{note}\n" + " ".join(mentions)
            await client.send_message(message.chat.id, text, parse_mode=ParseMode.HTML)
            mentions.clear()
            await asyncio.sleep(1)
    if mentions:
        text = f"{note}\n" + " ".join(mentions)
        await client.send_message(message.chat.id, text, parse_mode=ParseMode.HTML)

    await log_to_channel(client, f"Tagall run by {message.from_user.id} in {message.chat.id}")


def register(app: Client):
    app.add_handler(MessageHandler(tagall, filters.command("tagall") & admin_filter))
