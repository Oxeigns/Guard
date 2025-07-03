import logging
from typing import Dict

from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message, ChatPermissions

from oxeign.utils.perms import is_admin

from oxeign.swagger.biomode import is_biomode
from oxeign.swagger.approvals import is_approved
from oxeign.swagger.warnings import (
    add_warning,
    clear_warnings,
    get_all_warnings,
)

BIO_KEYWORDS = ["t.me", "joinchat", "onlyfans", "wa.me", "http", "https"]
logger = logging.getLogger(__name__)




async def check_bio(client: Client, message: Message) -> None:
    if message.chat.type not in ("group", "supergroup"):
        return
    if not message.from_user:
        return
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_biomode(chat_id):
        return
    if await is_admin(client, chat_id, user_id):
        return
    if await is_approved(chat_id, user_id):
        return
    try:
        user_chat = await client.get_chat(user_id)
        bio = user_chat.bio or ""
    except Exception:
        bio = ""
    lower_bio = bio.lower()
    if any(key in lower_bio for key in BIO_KEYWORDS):
        warns = await add_warning(chat_id, user_id)
        logger.info(
            "Bio warning %s/%s for user %s in chat %s",
            warns,
            3,
            user_id,
            chat_id,
        )
        if warns >= 3:
            try:
                await client.restrict_chat_member(
                    chat_id, user_id, ChatPermissions(can_send_messages=False)
                )
            except Exception as exc:
                logger.warning("Failed to mute user %s: %s", user_id, exc)
            await message.chat.send_message(
                "🚫 You’ve been muted for having a spammy bio."
            )
        else:
            await message.chat.send_message(
                f"⚠️ Warning {warns}/3 – Please remove bio link or you’ll be muted."
            )


async def clearwarn(client: Client, message: Message) -> None:
    if message.chat.type not in ("group", "supergroup"):
        return
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return
    target = None
    if message.reply_to_message:
        target = message.reply_to_message.from_user
    else:
        parts = message.text.split(maxsplit=1)
        if len(parts) > 1:
            try:
                target = await client.get_chat(parts[1])
            except Exception:
                await message.reply_text("User not found")
                return
    if not target:
        await message.reply_text("Reply to a user or specify a username/ID")
        return
    await clear_warnings(message.chat.id, target.id)
    await message.reply_html(f"Cleared warnings for {target.mention_html()}")


async def warnlist(client: Client, message: Message) -> None:
    if message.chat.type not in ("group", "supergroup"):
        return
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return
    warns: Dict[int, int] = await get_all_warnings(message.chat.id)
    if not warns:
        await message.reply_text("No warnings.")
        return
    lines = ["Current warnings:"]
    for uid, count in warns.items():
        try:
            user = await client.get_chat(uid)
            mention = user.mention_html()
        except Exception:
            mention = str(uid)
        lines.append(f"- {mention}: {count}")
    await message.reply_html("\n".join(lines))


def register(app: Client) -> None:
    app.add_handler(MessageHandler(check_bio, filters.group & ~filters.service))
    app.add_handler(MessageHandler(clearwarn, filters.command("clearwarn") & filters.group))
    app.add_handler(MessageHandler(warnlist, filters.command("warnlist") & filters.group))

