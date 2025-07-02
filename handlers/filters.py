import re
from pyrogram import Client, filters
from utils.perms import is_admin
from utils.logger import log_to_channel
from database.biomode import is_biomode
from config import BOT_NAME

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

    if LINK_RE.search(lower):
        await message.delete()
        await log_to_channel(client, f"{BOT_NAME}: Deleted link from {message.from_user.mention}")
        return

    if message.chat.username and f"@{message.chat.username.lower()}" in lower:
        await message.delete()
        await log_to_channel(client, f"{BOT_NAME}: Removed username mention from {message.from_user.mention}")
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

    if message.media and message.media != "message":
        await message.delete()
        await log_to_channel(client, f"{BOT_NAME}: Deleted media from {message.from_user.mention}")


async def check_edit(client: Client, message):
    if not message.from_user or await is_admin(client, message.chat.id, message.from_user.id):
        return
    await message.delete()
    await log_to_channel(client, f"{BOT_NAME}: Deleted edited message from {message.from_user.mention}")


def register(app: Client):
    app.on_message(filters.group & ~filters.service)(check_message)
    app.on_edited_message(filters.group)(check_edit)
