import logging
import re
from typing import Dict

from telegram import Update, ChatPermissions, ChatMemberStatus
from telegram.ext import (
    Application,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    filters,
)

from oxeign.config import OWNER_ID
from oxeign.swagger.biomode import is_biomode
from oxeign.swagger.approvals import is_approved
from oxeign.swagger.warnings import (
    add_warning,
    clear_warnings,
    get_all_warnings,
)

BIO_KEYWORDS = ["t.me", "joinchat", "onlyfans", "wa.me", "http", "https"]
logger = logging.getLogger(__name__)


async def _is_admin(context: CallbackContext, chat_id: int, user_id: int) -> bool:
    if user_id == OWNER_ID:
        return True
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
    except Exception:
        return False
    return member.status in (
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER,
    )


async def check_bio(update: Update, context: CallbackContext) -> None:
    if update.effective_chat is None or update.effective_user is None:
        return
    if update.effective_chat.type not in ("group", "supergroup"):
        return
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if not await is_biomode(chat_id):
        return
    if await _is_admin(context, chat_id, user_id):
        return
    if await is_approved(chat_id, user_id):
        return
    try:
        user_chat = await context.bot.get_chat(user_id)
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
                await context.bot.restrict_chat_member(
                    chat_id, user_id, ChatPermissions(can_send_messages=False)
                )
            except Exception as exc:
                logger.warning("Failed to mute user %s: %s", user_id, exc)
            await update.effective_chat.send_message(
                "🚫 You’ve been muted for having a spammy bio."
            )
        else:
            await update.effective_chat.send_message(
                f"⚠️ Warning {warns}/3 – Please remove bio link or you’ll be muted."
            )


async def clearwarn(update: Update, context: CallbackContext) -> None:
    if update.effective_chat is None or update.effective_user is None:
        return
    chat_id = update.effective_chat.id
    if not await _is_admin(context, chat_id, update.effective_user.id):
        return
    target = None
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
    elif context.args:
        try:
            target = await context.bot.get_chat(context.args[0])
        except Exception:
            await update.message.reply_text("User not found")
            return
    if not target:
        await update.message.reply_text("Reply to a user or specify a username/ID")
        return
    await clear_warnings(chat_id, target.id)
    await update.message.reply_html(f"Cleared warnings for {target.mention_html()}")


async def warnlist(update: Update, context: CallbackContext) -> None:
    if update.effective_chat is None or update.effective_user is None:
        return
    chat_id = update.effective_chat.id
    if not await _is_admin(context, chat_id, update.effective_user.id):
        return
    warns: Dict[int, int] = await get_all_warnings(chat_id)
    if not warns:
        await update.message.reply_text("No warnings.")
        return
    lines = ["Current warnings:"]
    for uid, count in warns.items():
        try:
            user = await context.bot.get_chat(uid)
            mention = user.mention_html()
        except Exception:
            mention = str(uid)
        lines.append(f"- {mention}: {count}")
    await update.message.reply_html("\n".join(lines))


def register(app: Application) -> None:
    app.add_handler(MessageHandler(filters.ALL & ~filters.StatusUpdate.ALL, check_bio))
    app.add_handler(CommandHandler("clearwarn", clearwarn))
    app.add_handler(CommandHandler("warnlist", warnlist))

