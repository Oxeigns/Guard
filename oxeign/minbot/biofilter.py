import logging
import re
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

# detect any obvious invite or external links in bios/messages
LINK_RE = re.compile(r"(https?://|t\.me|telegram\.me|wa\.me|joinchat|onlyfans)", re.I)


def has_spam_link(text: str) -> bool:
    """Return True if the text contains a spam or invite link."""
    return bool(LINK_RE.search(text))


logger = logging.getLogger(__name__)


async def _warn(
    client: Client, chat_id: int, user_id: int, message: Message, reason: str
) -> None:
    warns = await add_warning(chat_id, user_id)
    logger.info(
        "%s warning %s/%s for user %s in chat %s",
        reason,
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
        await message.chat.send_message("🚫 You’ve been muted for spam.")
    else:
        await message.chat.send_message(
            f"⚠️ Warning {warns}/3 – Stop posting spam links or you’ll be muted."
        )


async def _process_user_bio(
    client: Client, chat_id: int, user_id: int, message: Message
) -> bool:
    if await is_admin(client, chat_id, user_id):
        return
    if await is_approved(chat_id, user_id):
        return
    try:
        user_chat = await client.get_users(user_id)
        bio = user_chat.bio or ""
    except Exception:
        bio = ""
    if has_spam_link(bio or ""):
        try:
            await message.delete()
        except Exception:
            pass
        await _warn(client, chat_id, user_id, message, "Bio")
        return True
    return False


async def _process_message_links(
    client: Client, chat_id: int, user_id: int, message: Message
) -> bool:
    if await is_admin(client, chat_id, user_id):
        return
    if await is_approved(chat_id, user_id):
        return
    text = message.text or message.caption or ""
    if has_spam_link(text):
        try:
            await message.delete()
        except Exception:
            pass
        await _warn(client, chat_id, user_id, message, "Message")
        return True
    return False


async def check_bio(client: Client, message: Message) -> None:
    if message.chat.type not in ("group", "supergroup"):
        return
    if not message.from_user:
        return
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_biomode(chat_id):
        return
    flagged = await _process_message_links(client, chat_id, user_id, message)
    flagged |= await _process_user_bio(client, chat_id, user_id, message)


async def check_new_members(client: Client, message: Message) -> None:
    if message.chat.type not in ("group", "supergroup"):
        return
    if not message.new_chat_members:
        return
    chat_id = message.chat.id
    if not await is_biomode(chat_id):
        return
    flagged = False
    for member in message.new_chat_members:
        if await _process_user_bio(client, chat_id, member.id, message):
            flagged = True
    if flagged:
        try:
            await message.delete()
        except Exception:
            pass


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
                target = await client.get_users(parts[1])
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
            user = await client.get_users(uid)
            mention = user.mention_html()
        except Exception:
            mention = str(uid)
        lines.append(f"- {mention}: {count}")
    await message.reply_html("\n".join(lines))


def register(app: Client) -> None:
    app.add_handler(MessageHandler(check_bio, filters.group & ~filters.service))
    app.add_handler(
        MessageHandler(check_new_members, filters.group & filters.new_chat_members)
    )
    app.add_handler(
        MessageHandler(clearwarn, filters.command("clearwarn") & filters.group)
    )
    app.add_handler(
        MessageHandler(warnlist, filters.command("warnlist") & filters.group)
    )
