import logging
from typing import Dict, Tuple

from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import ChatPermissions, Message

from oxeign.utils.perms import is_admin
from oxeign.swagger.biomode import is_biomode
from oxeign.swagger.approvals import is_approved

logger = logging.getLogger(__name__)

# track warnings per (chat_id, user_id)
user_warnings: Dict[Tuple[int, int], int] = {}


async def bio_filter(client: Client, message: Message) -> None:
    """Warn and eventually mute users that have any bio set."""
    if message.chat.type not in ("group", "supergroup"):
        return
    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    # only run when biomode is enabled
    if not await is_biomode(chat_id):
        return

    # admins and approved users are ignored
    if await is_admin(client, chat_id, user_id):
        return
    if await is_approved(chat_id, user_id):
        return

    try:
        full_user = await client.get_users(user_id)
    except Exception as exc:  # pragma: no cover - network failures
        logger.error("Failed to fetch user %s bio: %s", user_id, exc)
        return

    if not full_user or not full_user.bio:
        return

    warn = user_warnings.get((chat_id, user_id), 0) + 1
    user_warnings[(chat_id, user_id)] = warn

    if warn < 3:
        await message.reply_text(f"⚠️ Warning {warn}/3: Bio not allowed here.")
    else:
        try:
            await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
        except Exception as exc:  # pragma: no cover - network failures
            logger.warning("Failed to mute user %s in %s: %s", user_id, chat_id, exc)
        await message.reply_text(
            "🚫 You have been muted for violating the bio policy."
        )


def register(app: Client) -> None:
    """Register the bio filter handler."""
    app.add_handler(MessageHandler(bio_filter, filters.group & filters.text))

