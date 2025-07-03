"""Bio and spam link filter with warnings and mute support.

This module requires **Pyrogram v2.x** and Python 3.10+. It should only run in
groups or supergroups where bio mode is enabled via :func:`is_biomode`. Admins
can approve users to bypass the filter. Warnings are persisted in MongoDB using
functions from :mod:`oxeign.swagger.warnings` and after exceeding
``MAX_WARNINGS`` the user will be muted.
"""

from __future__ import annotations

import logging
import re
from typing import Dict

from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import ChatPermissions, Message

from oxeign.utils.perms import is_admin
from oxeign.swagger.biomode import is_biomode
from oxeign.swagger.approvals import is_approved
from oxeign.swagger.warnings import (
    add_warning,
    clear_warnings,
    get_all_warnings,
)

logger = logging.getLogger(__name__)

# number of warnings before muting
MAX_WARNINGS = 3

# detect obvious invite or spam links in bios/messages
LINK_RE = re.compile(r"(https?://|t\.me|telegram\.me|wa\.me|joinchat|onlyfans)", re.I)


def has_spam_link(text: str) -> bool:
    """Return ``True`` if ``text`` contains an invite or spam link."""

    return bool(LINK_RE.search(text))


async def _warn(client: Client, chat_id: int, user_id: int, message: Message, reason: str) -> None:
    warns = await add_warning(chat_id, user_id)
    logger.info("%s warning %s/%s for user %s in chat %s", reason, warns, MAX_WARNINGS, user_id, chat_id)
    if warns >= MAX_WARNINGS:
        try:
            await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
        except Exception as exc:  # pragma: no cover - network failures
            logger.warning("Failed to mute user %s in %s: %s", user_id, chat_id, exc)
        await message.chat.send_message("🚫 You have been muted for spam.")
    else:
        await message.chat.send_message(
            f"⚠️ Warning {warns}/{MAX_WARNINGS} – Stop posting spam links or you'll be muted."
        )


async def _process_user_bio(client: Client, chat_id: int, user_id: int, message: Message) -> bool:
    if await is_admin(client, chat_id, user_id):
        return False
    if await is_approved(chat_id, user_id):
        return False
    try:
        user_chat = await client.get_users(user_id)
        bio = user_chat.bio or ""
    except Exception:  # pragma: no cover - network failures
        bio = ""
    if has_spam_link(bio):
        try:
            await message.delete()
        except Exception:
            pass
        await _warn(client, chat_id, user_id, message, "Bio")
        return True
    return False


async def _process_message_links(client: Client, chat_id: int, user_id: int, message: Message) -> bool:
    if await is_admin(client, chat_id, user_id):
        return False
    if await is_approved(chat_id, user_id):
        return False
    text = message.text or message.caption or ""
    if has_spam_link(text):
        try:
            await message.delete()
        except Exception:
            pass
        await _warn(client, chat_id, user_id, message, "Message")
        return True
    return False


async def bio_filter(client: Client, message: Message) -> None:
    if message.chat.type not in ("group", "supergroup"):
        return
    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_biomode(chat_id):
        return

    await _process_message_links(client, chat_id, user_id, message)
    await _process_user_bio(client, chat_id, user_id, message)


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
    """Register handlers for the bio filter system."""

    app.add_handler(MessageHandler(bio_filter, filters.group & ~filters.service))
    app.add_handler(MessageHandler(check_new_members, filters.group & filters.new_chat_members))
    app.add_handler(MessageHandler(clearwarn, filters.command("clearwarn") & filters.group))
    app.add_handler(MessageHandler(warnlist, filters.command("warnlist") & filters.group))

