import re
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler, EditedMessageHandler
from oxeign.utils.perms import is_admin
from oxeign.utils.logger import log_to_channel
from oxeign.swagger.biomode import is_biomode
from oxeign.swagger.settings import get_settings
from oxeign.config import BOT_NAME
try:
    from detoxify import Detoxify
    _tox = Detoxify("original")
except Exception:
    _tox = None

BAD_WORDS = {"badword", "spam"}
LINK_RE = re.compile(r"https?://|t\.me|telegram\.me")


async def check_message(client: Client, message):
    if not message.from_user or await is_admin(client, message.chat.id, message.from_user.id):
        return
    text = message.text or message.caption or ""
    lower = text.lower()

    if any(word in lower for word in BAD_WORDS):
        await message.delete()
        await log_to_channel(client, f"{BOT_NAME}: Deleted bad word from {message.from_user.mention}")
        return
    if _tox:
        try:
            scores = _tox.predict(text)
            if max(scores.values()) > 0.7:
                await message.delete()
                await log_to_channel(client, f"{BOT_NAME}: Deleted toxic message from {message.from_user.mention}")
                return
        except Exception:
            pass

    if LINK_RE.search(lower):
        await message.delete()
        await log_to_channel(client, f"{BOT_NAME}: Deleted link from {message.from_user.mention}")
        return

    if message.chat.username and f"@{message.chat.username.lower()}" in lower:
        await message.delete()
        await log_to_channel(client, f"{BOT_NAME}: Removed username mention from {message.from_user.mention}")
        return

    settings = await get_settings(message.chat.id)
    if settings.get("mode") != "off" and len(text) > settings.get("limit"):
        await message.delete()
        await log_to_channel(client, f"{BOT_NAME}: Deleted long message from {message.from_user.mention}")
        return

    if await is_biomode(message.chat.id):
        try:
            user = await client.get_users(message.from_user.id)
        except Exception:
            return
        if user.bio and LINK_RE.search(user.bio.lower()):
            await message.delete()
            await log_to_channel(client, f"{BOT_NAME}: Deleted message due to bio link from {message.from_user.mention}")
            return

    # Delete any message containing media (photo, video, sticker, etc.)
    # since this bot is focused on text based interactions only
    if message.media:
        await message.delete()
        await log_to_channel(client, f"{BOT_NAME}: Deleted media from {message.from_user.mention}")


async def check_edit(client: Client, message):
    if not message.from_user or await is_admin(client, message.chat.id, message.from_user.id):
        return
    await message.delete()
    await log_to_channel(client, f"{BOT_NAME}: Deleted edited message from {message.from_user.mention}")


def register(app: Client):
    app.add_handler(MessageHandler(check_message, filters.group & ~filters.service))
    app.add_handler(EditedMessageHandler(check_edit, filters.group))
