from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.enums import ParseMode
from oxeign.utils.filters import admin_filter
from oxeign.utils.logger import log_to_channel
import asyncio


async def tag_all(client: Client, message):
    if not message.chat or not message.from_user:
        return
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else ""
    mentions = []
    async for member in client.get_chat_members(message.chat.id):
        user = member.user
        if not user or user.is_bot or user.is_deleted:
            continue
        mentions.append(user.mention)
        if len(mentions) == 5:
            await message.reply(f"{text}\n" + " ".join(mentions), parse_mode=ParseMode.HTML)
            await asyncio.sleep(0.5)
            mentions.clear()
    if mentions:
        await message.reply(f"{text}\n" + " ".join(mentions), parse_mode=ParseMode.HTML)
    await log_to_channel(client, f"Tagall by {message.from_user.id} in {message.chat.id}")


def register(app: Client):
    app.add_handler(MessageHandler(tag_all, filters.command("tagall") & admin_filter))
