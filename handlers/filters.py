import asyncio
import logging
import re
from contextlib import suppress
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import (
    Message, ChatPermissions, InlineKeyboardButton,
    InlineKeyboardMarkup, CallbackQuery
)

from utils.errors import catch_errors
from utils.perms import is_admin
from utils.db import (
    get_setting,
    set_setting,
    get_bio_filter,
    increment_warning,
    reset_warning,
    is_approved,
)

logger = logging.getLogger(__name__)

# Detect common links such as http, https, t.me, bit.ly and generic domains
LINK_RE = re.compile(
    r"(https?://\S+|t\.me/\S+|bit\.ly/\S+|tg://\S+|(?:[\w-]+\.)+\w{2,})",
    re.IGNORECASE,
)
MAX_BIO_LENGTH = 800
SUPPORT_CHAT = "https://t.me/botsyard"


def mention_html(user) -> str:
    return f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"


def contains_link(text: str) -> bool:
    return bool(LINK_RE.search(text or ""))


def build_warning(count: int, user, is_final: bool = False):
    name = f"@{user.username}" if user.username else f"{user.first_name} ({user.id})"
    support_btn = InlineKeyboardButton("📨 Support", url=SUPPORT_CHAT)

    if is_final:
        msg = (
            f"🔇 <b>Final Warning for {name}</b>\n\n"
            "Your bio contains a link or is too long.\n"
            "You have been <b>muted</b>.\n"
            "Fix your bio and contact support or an admin."
        )
        kb = InlineKeyboardMarkup([
            [support_btn],
            [InlineKeyboardButton("🔓 Unmute", callback_data=f"biofilter_unmute_{user.id}")]
        ])
    else:
        msg = (
            f"⚠️ <b>Warning {count}/3 for {name}</b>\n\n"
            "Your bio contains a link or is too long.\n"
            "Fix it before you're muted."
        )
        kb = InlineKeyboardMarkup([[support_btn]])

    return msg, kb


async def warn_user(client: Client, chat_id: int, user) -> None:
    """Issue a warning and ban if the limit is reached."""
    count = await increment_warning(chat_id, user.id)
    limit = int(await get_setting(chat_id, "warn_limit", "3"))
    mention = mention_html(user)
    if count >= limit:
        with suppress(Exception):
            await client.ban_chat_member(chat_id, user.id)
        await reset_warning(chat_id, user.id)
        await client.send_message(
            chat_id,
            f"🚫 {mention} banned after {limit} warnings.",
            parse_mode=ParseMode.HTML,
        )
    else:
        await client.send_message(
            chat_id,
            f"⚠️ Warning {count}/{limit} for {mention}",
            parse_mode=ParseMode.HTML,
        )


def register(app: Client) -> None:

    @app.on_message(filters.group & (filters.text | filters.caption))
    @catch_errors
    async def check_message_bio(client: Client, message: Message):
        user = message.from_user
        chat_id = message.chat.id

        if not user or user.is_bot:
            return

        try:
            if not await get_bio_filter(chat_id):
                return
        except Exception as e:  # noqa: BLE001
            logger.warning("Error fetching bio filter for chat %s: %s", chat_id, e)
            return

        if await is_admin(client, message, user.id) or await is_approved(chat_id, user.id):
            return

        try:
            user_info = await client.get_chat(user.id)
            bio = getattr(user_info, "bio", "")
        except Exception as e:  # noqa: BLE001
            logger.warning("Failed to fetch bio for user %s: %s", user.id, e)
            return

        if not bio or (len(bio) <= MAX_BIO_LENGTH and not contains_link(bio)):
            return

        punishment = await get_setting(chat_id, "punish_biolink", "delete")
        with suppress(Exception):
            await message.delete()

        if punishment == "ban":
            with suppress(Exception):
                await client.ban_chat_member(chat_id, user.id)
            return

        if punishment == "warn":
            await warn_user(client, chat_id, user)
        # delete action already performed above

    @app.on_message(filters.new_chat_members)
    @catch_errors
    async def check_new_member_bio(client: Client, message: Message):
        chat_id = message.chat.id

        if not await get_bio_filter(chat_id):
            return

        for user in message.new_chat_members:
            if user.is_bot or await is_admin(client, message, user.id) or await is_approved(chat_id, user.id):
                continue

            try:
                user_info = await client.get_chat(user.id)
                bio = getattr(user_info, "bio", "")
            except Exception as e:  # noqa: BLE001
                logger.warning("Couldn't fetch bio for new member %s: %s", user.id, e)
                continue

            if not bio or (len(bio) <= MAX_BIO_LENGTH and not contains_link(bio)):
                continue

            punishment = await get_setting(chat_id, "punish_biolink", "delete")
            with suppress(Exception):
                await message.delete()

            if punishment == "ban":
                with suppress(Exception):
                    await client.ban_chat_member(chat_id, user.id)
                continue

            if punishment == "warn":
                await warn_user(client, chat_id, user)

    @app.on_callback_query(filters.regex(r"^biofilter_unmute_(\d+)$"))
    @catch_errors
    async def unmute_user_cb(client: Client, query: CallbackQuery):
        user_id = int(query.data.split("_")[-1])
        chat_id = query.message.chat.id

        if not await is_admin(client, query.message, query.from_user.id):
            await query.answer("Only admins can unmute users.", show_alert=True)
            return

        try:
            await client.restrict_chat_member(
                chat_id,
                user_id,
                ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_polls=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_invite_users=True,
                ),
            )
            await query.answer("✅ User unmuted.")
            await query.message.reply_text(
                f"🔓 User <a href='tg://user?id={user_id}'>unmuted</a>.",
                parse_mode=ParseMode.HTML,
            )
        except Exception as e:  # noqa: BLE001
            logger.error("Error while unmuting user %s: %s", user_id, e)
            await query.answer("❌ Could not unmute user.")

    async def delete_later(
        chat_id: int, message_id: int, delay: int, notify: bool = False
    ) -> None:
        await asyncio.sleep(delay)
        with suppress(Exception):
            await app.delete_messages(chat_id, message_id)
        if notify:
            with suppress(Exception):
                note = await app.send_message(
                    chat_id,
                    "⚠️ This edited message was auto-deleted as per group rules.",
                )
                await asyncio.sleep(15)
                await note.delete()

    @app.on_message(filters.group & ~filters.service)
    @catch_errors
    async def enforce_filters(client: Client, message: Message):
        text = message.text or message.caption or ""
        chat_id = message.chat.id
        user = message.from_user

        if user and await is_admin(client, message, user.id):
            pass
        else:
            if (
                await get_setting(chat_id, "linkfilter", "0") == "1"
                and LINK_RE.search(text)
            ):
                punishment = await get_setting(chat_id, "punish_linkfilter", "delete")
                with suppress(Exception):
                    await message.delete()
                if punishment == "ban":
                    with suppress(Exception):
                        await client.ban_chat_member(chat_id, user.id)
                elif punishment == "warn":
                    await warn_user(client, chat_id, user)
                return

            if (
                await get_setting(chat_id, "biolink", "0") == "1"
                and user is not None
            ):
                try:
                    u = await client.get_users(user.id)
                    if u.bio and LINK_RE.search(u.bio):
                        punishment = await get_setting(chat_id, "punish_biolink", "delete")
                        with suppress(Exception):
                            await message.delete()
                        if punishment == "ban":
                            with suppress(Exception):
                                await client.ban_chat_member(chat_id, user.id)
                        elif punishment == "warn":
                            await warn_user(client, chat_id, user)
                        return
                except Exception:
                    pass

        if await get_setting(chat_id, "autodelete", "0") == "1":
            delay = int(await get_setting(chat_id, "autodelete_interval", "30"))
            asyncio.create_task(delete_later(chat_id, message.id, delay))

    @app.on_edited_message(filters.group & ~filters.service)
    @catch_errors
    async def on_edit(client: Client, message: Message):
        if await get_setting(message.chat.id, "editmode", "0") == "1":
            delay = int(await get_setting(message.chat.id, "autodelete_interval", "900"))
            asyncio.create_task(delete_later(message.chat.id, message.id, delay, notify=True))
