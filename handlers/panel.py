import logging
from time import perf_counter
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatType
from pyrogram.types import (
    Message, CallbackQuery, ChatPermissions,
    InlineKeyboardMarkup, InlineKeyboardButton
)

import config
from utils.perms import is_admin
from utils.errors import catch_errors
from utils.db import (
    get_bio_filter, toggle_bio_filter, set_bio_filter,
    get_autodelete, set_autodelete
)

logger = logging.getLogger(__name__)

BOT_USERNAME = getattr(config, "BOT_USERNAME", "YourBot")
SUPPORT_CHAT_URL = getattr(config, "SUPPORT_CHAT_URL", "https://t.me/botsyard")
DEVELOPER_URL = getattr(config, "DEVELOPER_URL", "https://t.me/botsyard")
BANNER_URL = getattr(config, "BANNER_URL", None)


# Util: Shorten display names
def elid(text: str, max_len: int = 25) -> str:
    return text if len(text) <= max_len else text[:max_len - 1] + "…"


# Panels
async def build_group_panel(chat_id: int) -> tuple[str, InlineKeyboardMarkup]:
    bio_status = await get_bio_filter(chat_id)
    delete_delay = await get_autodelete(chat_id)

    caption = (
        "<b>🛡️ Group Guard Panel</b>\n\n"
        f"🔗 Bio Filter: {'<b>✅ ON</b>' if bio_status else '<b>❌ OFF</b>'}\n"
        f"🗑️ Auto Delete: {'<b>✅ {delete_delay}s</b>' if delete_delay else '<b>❌ OFF</b>'}"
    )

    buttons = [
        [
            InlineKeyboardButton("✅ Approve", callback_data="cb_approve"),
            InlineKeyboardButton("🚫 Unapprove", callback_data="cb_unapprove"),
        ],
        [
            InlineKeyboardButton("🧹 Auto-Delete", callback_data="cb_toggle_autodel"),
            InlineKeyboardButton("🔗 Bio Filter", callback_data="cb_biolink_toggle"),
        ],
        [
            InlineKeyboardButton("📖 Help", callback_data="cb_help"),
            InlineKeyboardButton("📡 Ping", callback_data="cb_ping"),
        ],
        [
            InlineKeyboardButton("👨‍💻 Dev", url=DEVELOPER_URL),
            InlineKeyboardButton("💬 Support", url=SUPPORT_CHAT_URL),
        ],
    ]
    return caption, InlineKeyboardMarkup(buttons)


async def build_private_panel() -> tuple[str, InlineKeyboardMarkup]:
    caption = (
        "<b>🤖 Bot Control Panel</b>\n\n"
        "Use the buttons to manage settings or get help."
    )
    buttons = [
        [
            InlineKeyboardButton("📖 Help", callback_data="cb_help"),
            InlineKeyboardButton("💬 Support", url=SUPPORT_CHAT_URL),
        ],
        [
            InlineKeyboardButton("👨‍💻 Developer", url=DEVELOPER_URL),
            InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true"),
        ],
    ]
    return caption, InlineKeyboardMarkup(buttons)


async def send_panel(client: Client, message: Message) -> None:
    is_private = message.chat.type == ChatType.PRIVATE
    caption, markup = await build_private_panel() if is_private else await build_group_panel(message.chat.id)

    try:
        if BANNER_URL:
            await client.send_photo(
                chat_id=message.chat.id,
                photo=BANNER_URL,
                caption=caption,
                reply_markup=markup,
                parse_mode=ParseMode.HTML
            )
            return
    except Exception as e:
        logger.warning("Banner failed: %s", e)

    await message.reply_text(caption, reply_markup=markup, parse_mode=ParseMode.HTML)


# Unified Handler Register
def register(app: Client) -> None:

    # Show start/help/menu
    @app.on_message(filters.command(["start", "help", "menu"]))
    @catch_errors
    async def handle_menu(client: Client, message: Message):
        await send_panel(client, message)

    # Ping test
    @app.on_callback_query(filters.regex(r"^cb_ping$"))
    @catch_errors
    async def cb_ping(client: Client, query: CallbackQuery):
        start = perf_counter()
        await query.answer("📡 Pinging...")
        latency = round((perf_counter() - start) * 1000, 2)
        await query.message.reply_text(f"🎉 Pong! <code>{latency}ms</code>", parse_mode=ParseMode.HTML)

    # Help screen
    @app.on_callback_query(filters.regex(r"^cb_help$"))
    @catch_errors
    async def cb_help(client: Client, query: CallbackQuery):
        await query.answer()
        help_text = (
            "<b>📖 Bot Commands</b>\n\n"
            "/approve – Approve user\n"
            "/unapprove – Remove approval\n"
            "/viewapproved – List approved users\n"
            "/setautodelete <sec>\n"
            "/autodeleteon | /autodeleteoff\n"
            "/mute | /kick | /ban\n"
            "/biolink on/off – Toggle bio filter"
        )
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="cb_back")]])
        await query.message.edit_text(help_text, reply_markup=markup, parse_mode=ParseMode.HTML)

    # Return to main panel
    @app.on_callback_query(filters.regex(r"^cb_back$"))
    @catch_errors
    async def cb_back(client: Client, query: CallbackQuery):
        await query.answer()
        caption, markup = await build_group_panel(query.message.chat.id)
        await query.message.edit_text(caption, reply_markup=markup, parse_mode=ParseMode.HTML)

    # Toggle bio filter
    @app.on_callback_query(filters.regex(r"^cb_biolink_toggle$"))
    @catch_errors
    async def cb_bio_toggle(client: Client, query: CallbackQuery):
        if not await is_admin(client, query.message, query.from_user.id):
            await query.answer("Admins only!", show_alert=True)
            return
        state = await toggle_bio_filter(query.message.chat.id)
        await query.answer(f"Bio Filter is now {'ON ✅' if state else 'OFF ❌'}")
        await cb_back(client, query)

    # Toggle auto-delete
    @app.on_callback_query(filters.regex(r"^cb_toggle_autodel$"))
    @catch_errors
    async def cb_toggle_autodel(client: Client, query: CallbackQuery):
        if not await is_admin(client, query.message, query.from_user.id):
            await query.answer("Admins only!", show_alert=True)
            return
        current = await get_autodelete(query.message.chat.id)
        new_val = 0 if current > 0 else 60
        await set_autodelete(query.message.chat.id, new_val)
        await query.answer(f"Auto-Delete is now {'ENABLED ✅' if new_val else 'DISABLED ❌'}")
        await cb_back(client, query)

    # Approve tip
    @app.on_callback_query(filters.regex(r"^cb_approve$"))
    @catch_errors
    async def cb_approve_tip(client: Client, query: CallbackQuery):
        await query.answer()
        await query.message.reply_text("✅ Reply to a user with /approve to allow them to speak.")

    # Unapprove tip
    @app.on_callback_query(filters.regex(r"^cb_unapprove$"))
    @catch_errors
    async def cb_unapprove_tip(client: Client, query: CallbackQuery):
        await query.answer()
        await query.message.reply_text("🚫 Reply to a user with /unapprove to remove access.")
