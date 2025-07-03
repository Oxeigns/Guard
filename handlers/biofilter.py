"""Bio filter and mute logic."""

import re
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, ChatPermissions

from utils.storage import Storage
from utils.perms import is_user_admin
from handlers.logs import log

storage = Storage()

LINK_RE = re.compile(r"https?://|t\.me|\.com|\.me|\.link|\.store|\.shop", re.I)
WARN_TEXT = {
    1: "⚠️ Warning 1",
    2: "⚠️ Warning 2",
    3: "⛔ Final Warning",
}


@Client.on_message(filters.command("biomode") & filters.group)
async def set_bio_mode(client: Client, message: Message) -> None:
    """Enable or disable bio filtering."""
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if not await is_user_admin(member):
        return
    if len(message.command) < 2:
        mode = (await storage.get_settings(message.chat.id)).get("biomode", True)
        text = "Bio mode is on" if mode else "Bio mode is off"
        await message.reply_text(text)
        return
    enabled = message.command[1].lower() in {"on", "yes", "enable", "true"}
    await storage.update_settings(message.chat.id, biomode=enabled)
    await message.reply_text("Bio mode enabled" if enabled else "Bio mode disabled")
    await log(
        client,
        f"🧹 Bio mode set to {enabled} in `{message.chat.id}` by `{message.from_user.id}`",
    )

@Client.on_message(filters.group & ~filters.service)
async def bio_scan(client: Client, message: Message) -> None:
    """Scan user bios for links."""
    settings = await storage.get_settings(message.chat.id)
    if not settings.get("biomode", True):
        return

    if not message.from_user or message.from_user.is_bot:
        return

    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if await is_user_admin(member):
        return
    if await storage.is_approved(message.chat.id, message.from_user.id):
        return

    bio = message.from_user.bio or ""
    if not LINK_RE.search(bio):
        return

    count = await storage.increment_warning(message.chat.id, message.from_user.id)
    await message.delete()
    await log(client, f"🧹 Deleted bio link message from `{message.from_user.id}` in `{message.chat.id}`")
    await message.chat.send_message(
        WARN_TEXT.get(count, WARN_TEXT[3]),
        reply_to_message_id=message.id,
        parse_mode=ParseMode.MARKDOWN,
    )

    await log(client, f"⚠️ User `{message.from_user.id}` warned ({count}) in `{message.chat.id}`")

    if count >= 3:
        await storage.reset_warnings(message.chat.id, message.from_user.id)
        await client.restrict_chat_member(
            message.chat.id,
            message.from_user.id,
            ChatPermissions(),
        )
        await log(client, f"🔇 Muted `{message.from_user.id}` in `{message.chat.id}`")

