import logging
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery

from config import (
    SUPPORT_CHAT_URL,
    DEVELOPER_URL,
    BANNER_URL,
)
from utils.errors import catch_errors
from utils.db import get_bio_filter, toggle_bio_filter
from utils.perms import is_admin

logger = logging.getLogger(__name__)


def elid(text: str, max_len: int = 25) -> str:
    """Return text truncated to ``max_len`` characters with an ellipsis."""
    return text if len(text) <= max_len else text[: max_len - 1] + "…"


async def build_group_panel(chat_id: int) -> tuple[str, InlineKeyboardMarkup]:
    status = await get_bio_filter(chat_id)
    caption = (
        "🗭️ *Guard Control Panel*\n\n"
        f"🔗 Bio Filter: {'✅ ON' if status else '❌ OFF'}"
    )

    buttons = [
        [
            InlineKeyboardButton("✅ Approve", callback_data="cb_approve"),
            InlineKeyboardButton("🚫 Unapprove", callback_data="cb_unapprove"),
        ],
        [
            InlineKeyboardButton("🗑️ AutoDelete", callback_data="cb_autodel"),
            InlineKeyboardButton(
                "🔗 Toggle Bio Filter", callback_data="cb_biolink_toggle"
            ),
        ],
        [
            InlineKeyboardButton("📖 Help", callback_data="help"),
            InlineKeyboardButton("📡 Ping", callback_data="ping"),
        ],
        [
            InlineKeyboardButton("👨‍💻 Developer", url=DEVELOPER_URL),
            InlineKeyboardButton("💬 Support", url=SUPPORT_CHAT_URL),
        ],
    ]

    return caption, InlineKeyboardMarkup(buttons)


async def build_private_panel() -> tuple[str, InlineKeyboardMarkup]:
    caption = (
        "*🤖 Bot Control Panel*\n\n"
        "Use the buttons below to manage the bot or get help."
    )

    buttons = [
        [
            InlineKeyboardButton("📖 Help", callback_data="help"),
            InlineKeyboardButton("💬 Support", url=SUPPORT_CHAT_URL),
        ],
        [
            InlineKeyboardButton("👨‍💻 Developer", url=DEVELOPER_URL),
            InlineKeyboardButton(
                "\u2795 Add me to Group",
                url="https://t.me/YOUR_BOT_USERNAME?startgroup=true",
            ),
        ],
    ]

    return caption, InlineKeyboardMarkup(buttons)


async def send_panel(client: Client, message: Message) -> None:
    is_private = message.chat.type == ChatType.PRIVATE

    if is_private:
        caption, markup = await build_private_panel()
    elif await is_admin(client, message):
        caption, markup = await build_group_panel(message.chat.id)
    else:
        await message.reply_text(
            "\u274c You must be an admin to use this command in groups."
        )
        return

    try:
        if BANNER_URL:
            await client.send_photo(
                chat_id=message.chat.id,
                photo=BANNER_URL,
                caption=caption,
                reply_markup=markup,
                parse_mode=ParseMode.MARKDOWN,
            )
            return
    except Exception as e:
        logger.warning("Failed to send image banner: %s", e)

    await message.reply_text(caption, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)


async def edit_panel(query: CallbackQuery) -> None:
    caption, markup = await build_group_panel(query.message.chat.id)
    await query.message.edit_text(caption, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)


def register(app: Client) -> None:
    @app.on_message(filters.command(["start", "help", "menu"]))
    @catch_errors
    async def start_menu(client: Client, message: Message):
        logger.info("Command %s from %s", message.text, message.chat.id)
        await send_panel(client, message)

    @app.on_callback_query(filters.regex(r"^help$"))
    @catch_errors
    async def help_cb(client: Client, query: CallbackQuery):
        logger.info("help callback from %s", query.from_user.id)
        help_text = (
            "*🧪‍💻 Commands Overview*\n\n"
            "\u2022 `/approve` \u2013 Approve a user\n"
            "\u2022 `/unapprove` \u2013 Unapprove a user\n"
            "\u2022 `/viewapproved` \u2013 List approved users\n"
            "\u2022 `/setautodelete <sec>` \u2013 Set auto-delete\n"
            "\u2022 `/mute` \u2013 Mute a user (reply)\n"
            "\u2022 `/kick` \u2013 Kick a user (reply)\n"
            "\u2022 `/biolink [on|off]` \u2013 Toggle bio filter\n"
        )
        markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("◀️ Back", callback_data="back_to_panel")]]
        )
        await query.message.edit_text(help_text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)

    @app.on_callback_query(filters.regex(r"^back_to_panel$"))
    @catch_errors
    async def back_cb(client: Client, query: CallbackQuery):
        await query.answer()
        await edit_panel(query)

    @app.on_callback_query(filters.regex(r"^cb_biolink_toggle$"))
    @catch_errors
    async def biolink_toggle_cb(client: Client, query: CallbackQuery):
        state = await toggle_bio_filter(query.message.chat.id)
        await query.answer(f"Bio Filter is now {'ON ✅' if state else 'OFF ❌'}")
        await edit_panel(query)

    @app.on_callback_query(filters.regex(r"^cb_approve$"))
    @catch_errors
    async def approve_info(client: Client, query: CallbackQuery):
        await query.answer()
        await query.message.reply_text(
            "\u2705 Reply to a user with `/approve` to whitelist them.",
            parse_mode=ParseMode.MARKDOWN,
        )

    @app.on_callback_query(filters.regex(r"^cb_unapprove$"))
    @catch_errors
    async def unapprove_info(client: Client, query: CallbackQuery):
        await query.answer()
        await query.message.reply_text(
            "🚫 Reply to a user with `/unapprove` to remove from whitelist.",
            parse_mode=ParseMode.MARKDOWN,
        )

    @app.on_callback_query(filters.regex(r"^cb_autodel$"))
    @catch_errors
    async def autodel_info(client: Client, query: CallbackQuery):
        await query.answer()
        await query.message.reply_text(
            "🗑️ Use `/setautodelete <seconds>` to auto-delete user messages.",
            parse_mode=ParseMode.MARKDOWN,
        )

    @app.on_callback_query(filters.regex(r"^ping$"))
    @catch_errors
    async def ping_cb(client: Client, query: CallbackQuery):
        from time import perf_counter

        start = perf_counter()
        await query.answer("📡 Pinging...")
        latency = round((perf_counter() - start) * 1000, 2)
        await query.message.reply_text(
            f"🎉 Pong! `{latency}ms`", parse_mode=ParseMode.MARKDOWN
        )
