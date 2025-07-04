"""Control panel with auto-delete toggle & modern UI."""

import logging
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery

import config
from utils.errors import catch_errors
from utils.db import get_bio_filter, toggle_bio_filter, get_autodelete, set_autodelete
from utils.perms import is_admin

logger = logging.getLogger(__name__)

BOT_USERNAME = getattr(config, "BOT_USERNAME", "YourBot")  # From config or fallback
SUPPORT_CHAT_URL = getattr(config, "SUPPORT_CHAT_URL", "https://t.me/botsyard")
DEVELOPER_URL = getattr(config, "DEVELOPER_URL", "https://t.me/botsyard")
BANNER_URL = getattr(config, "BANNER_URL", None)


def elid(text: str, max_len: int = 25) -> str:
    return text if len(text) <= max_len else text[: max_len - 1] + "…"


async def build_group_panel(chat_id: int) -> tuple[str, InlineKeyboardMarkup]:
    bio_status = await get_bio_filter(chat_id)
    delete_delay = await get_autodelete(chat_id)

    caption = (
        "<b>🛡️ Guard Control Panel</b>\n\n"
        f"🔗 Bio Filter: {'<b>✅ ON</b>' if bio_status else '<b>❌ OFF</b>'}\n"
        f"🗑️ Auto Delete: {'<b>✅ Enabled</b>' if delete_delay > 0 else '<b>❌ Disabled</b>'}"
    )

    buttons = [
        [
            InlineKeyboardButton("✅ Approve", callback_data="cb_approve"),
            InlineKeyboardButton("🚫 Unapprove", callback_data="cb_unapprove"),
        ],
        [
            InlineKeyboardButton("🔁 Toggle Auto-Delete", callback_data="cb_toggle_autodel"),
            InlineKeyboardButton("🔗 Toggle Bio Filter", callback_data="cb_biolink_toggle"),
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
        "<b>🤖 Bot Control Panel</b>\n\n"
        "Use the buttons below to manage the bot or get help."
    )
    buttons = [
        [
            InlineKeyboardButton("📖 Help", callback_data="help"),
            InlineKeyboardButton("💬 Support", url=SUPPORT_CHAT_URL),
        ],
        [
            InlineKeyboardButton("👨‍💻 Developer", url=DEVELOPER_URL),
            InlineKeyboardButton("➕ Add me to Group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true"),
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
                parse_mode=ParseMode.HTML,
            )
            return
    except Exception as e:
        logger.warning("Failed to send image banner: %s", e)

    await message.reply_text(caption, reply_markup=markup, parse_mode=ParseMode.HTML)


async def edit_panel(query: CallbackQuery) -> None:
    caption, markup = await build_group_panel(query.message.chat.id)
    await query.message.edit_text(caption, reply_markup=markup, parse_mode=ParseMode.HTML)


async def send_tip(query: CallbackQuery, text: str):
    await query.answer()
    await query.message.reply_text(text, parse_mode=ParseMode.HTML)


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
        await query.answer()
        help_text = (
            "<b>🧾 Command Overview</b>\n\n"
            "• <code>/approve</code> – Approve user\n"
            "• <code>/unapprove</code> – Unapprove user\n"
            "• <code>/viewapproved</code> – List approved users\n"
            "• <code>/setautodelete &lt;sec&gt;</code> – Auto delete delay\n"
            "• <code>/autodeleteon</code> / <code>/autodeleteoff</code>\n"
            "• <code>/biolink [on|off]</code> – Toggle bio filter\n"
        )
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="back_to_panel")]])
        try:
            await query.message.edit_text(help_text, reply_markup=markup, parse_mode=ParseMode.HTML)
        except Exception:
            logger.debug("Help text not modified")

    @app.on_callback_query(filters.regex(r"^back_to_panel$"))
    @catch_errors
    async def back_cb(client: Client, query: CallbackQuery):
        await query.answer()
        await edit_panel(query)

    @app.on_callback_query(filters.regex(r"^cb_biolink_toggle$"))
    @catch_errors
    async def toggle_bio_cb(client: Client, query: CallbackQuery):
        if not await is_admin(client, query.message, query.from_user.id):
            await query.answer("Admins only!", show_alert=True)
            return
        state = await toggle_bio_filter(query.message.chat.id)
        await query.answer(f"Bio Filter is now {'ON ✅' if state else 'OFF ❌'}")
        await edit_panel(query)

    @app.on_callback_query(filters.regex(r"^cb_toggle_autodel$"))
    @catch_errors
    async def toggle_autodel_cb(client: Client, query: CallbackQuery):
        if not await is_admin(client, query.message, query.from_user.id):
            await query.answer("Admins only!", show_alert=True)
            return

        current = await get_autodelete(query.message.chat.id)
        new_value = 0 if current > 0 else 60  # Toggle
        await set_autodelete(query.message.chat.id, new_value)

        status = "enabled ✅" if new_value > 0 else "disabled ❌"
        await query.answer(f"Auto-Delete is now {status}")
        await edit_panel(query)

    @app.on_callback_query(filters.regex(r"^cb_approve$"))
    @catch_errors
    async def cb_approve_tip(client: Client, query: CallbackQuery):
        await send_tip(query, "✅ Reply to a user with <code>/approve</code> to approve them.")

    @app.on_callback_query(filters.regex(r"^cb_unapprove$"))
    @catch_errors
    async def cb_unapprove_tip(client: Client, query: CallbackQuery):
        await send_tip(query, "🚫 Reply with <code>/unapprove</code> to remove user approval.")

    @app.on_callback_query(filters.regex(r"^cb_autodel$"))
    @catch_errors
    async def cb_autodel_tip(client: Client, query: CallbackQuery):
        await send_tip(query, "🗑️ Use <code>/setautodelete &lt;seconds&gt;</code> to auto-delete user messages.")

    @app.on_callback_query(filters.regex(r"^ping$"))
    @catch_errors
    async def ping_cb(client: Client, query: CallbackQuery):
        from time import perf_counter
        start = perf_counter()
        await query.answer("📡 Pinging...")
        latency = round((perf_counter() - start) * 1000, 2)
        await query.message.reply_text(f"🎉 Pong! <code>{latency}ms</code>", parse_mode=ParseMode.HTML)
