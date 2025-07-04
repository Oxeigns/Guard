import logging
from time import perf_counter
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatType
from pyrogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)

from utils.errors import catch_errors
from oxygenbot import get_setting, toggle_setting, set_setting  # assumed imports from your DB logic
from utils.perms import is_admin

logger = logging.getLogger(__name__)

BOT_USERNAME = "OxeignBot"
SUPPORT_CHAT_URL = "https://t.me/botsyard"
DEVELOPER_URL = "https://t.me/botsyard"
BANNER_URL = None


async def build_group_panel(chat_id: int) -> tuple[str, InlineKeyboardMarkup]:
    bio_status = await get_setting(chat_id, "biolink", "0") == "1"
    delete_enabled = await get_setting(chat_id, "autodelete", "0") == "1"
    delete_interval = await get_setting(chat_id, "autodelete_interval", "0")

    caption = (
        "<b>🛡️ Group Guard Panel</b>\n\n"
        f"🔗 Bio Filter: {'<b>✅ ON</b>' if bio_status else '<b>❌ OFF</b>'}\n"
        f"🗑️ Auto Delete: {'<b>✅ ' + delete_interval + 's</b>' if delete_enabled and delete_interval else '<b>❌ OFF</b>'}"
    )

    buttons = [
        [
            InlineKeyboardButton("✅ Approve", callback_data="cb_approve"),
            InlineKeyboardButton("🚫 Unapprove", callback_data="cb_unapprove"),
        ],
        [
            InlineKeyboardButton("🧹 Auto-Delete", callback_data="cb_toggle_autodel"),
            InlineKeyboardButton("🔗 Bio Filter", callback_data="cb_toggle_biolink"),
        ],
        [
            InlineKeyboardButton("📖 Help", callback_data="cb_help"),
            InlineKeyboardButton("📡 Ping", callback_data="cb_ping"),
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
        "Use the buttons below to manage settings or get help."
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
    if message.chat.type == ChatType.PRIVATE:
        caption, markup = await build_private_panel()
    else:
        caption, markup = await build_group_panel(message.chat.id)

    try:
        if BANNER_URL:
            await client.send_photo(
                chat_id=message.chat.id,
                photo=BANNER_URL,
                caption=caption,
                reply_markup=markup,
                parse_mode=ParseMode.HTML
            )
        else:
            await message.reply_text(caption, reply_markup=markup, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.warning("Banner failed: %s", e)
        await message.reply_text(caption, reply_markup=markup, parse_mode=ParseMode.HTML)


def register(app: Client) -> None:

    @app.on_message(filters.command(["start", "menu", "help"]))
    @catch_errors
    async def handle_menu(client: Client, message: Message):
        await send_panel(client, message)

    @app.on_callback_query()
    @catch_errors
    async def callback_handler(client: Client, query: CallbackQuery):
        data = query.data
        chat_id = query.message.chat.id
        user_id = query.from_user.id

        if data == "cb_ping":
            start = perf_counter()
            await query.answer("📡 Pinging...")
            latency = round((perf_counter() - start) * 1000, 2)
            await query.message.reply_text(f"🎉 Pong! <code>{latency}ms</code>", parse_mode=ParseMode.HTML)

        elif data == "cb_help":
            await query.answer()
            help_text = (
                "<b>📖 Bot Commands</b>\n\n"
                "/approve – Approve user\n"
                "/unapprove – Revoke approval\n"
                "/viewapproved – List approved users\n"
                "/setautodelete <seconds>\n"
                "/autodeleteon | /autodeleteoff\n"
                "/mute | /kick | /ban\n"
                "/biolink on/off – Toggle bio link filter"
            )
            markup = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="cb_back")]])
            await query.message.edit_text(help_text, reply_markup=markup, parse_mode=ParseMode.HTML)

        elif data == "cb_back":
            await query.answer()
            caption, markup = await build_group_panel(chat_id)
            await query.message.edit_text(caption, reply_markup=markup, parse_mode=ParseMode.HTML)

        elif data == "cb_toggle_biolink":
            if not await is_admin(client, query.message, user_id):
                await query.answer("Admins only!", show_alert=True)
                return
            state = await toggle_setting(chat_id, "biolink")
            await query.answer(f"Bio Filter is now {'ON ✅' if state == '1' else 'OFF ❌'}")
            caption, markup = await build_group_panel(chat_id)
            await query.message.edit_text(caption, reply_markup=markup, parse_mode=ParseMode.HTML)

        elif data == "cb_toggle_autodel":
            if not await is_admin(client, query.message, user_id):
                await query.answer("Admins only!", show_alert=True)
                return
            current = await get_setting(chat_id, "autodelete", "0")
            new_value = "0" if current == "1" else "1"
            await set_setting(chat_id, "autodelete", new_value)
            await set_setting(chat_id, "autodelete_interval", "60" if new_value == "1" else "0")
            await query.answer(f"Auto-Delete is now {'ENABLED ✅' if new_value == '1' else 'DISABLED ❌'}")
            caption, markup = await build_group_panel(chat_id)
            await query.message.edit_text(caption, reply_markup=markup, parse_mode=ParseMode.HTML)

        elif data == "cb_approve":
            await query.answer()
            await query.message.reply_text("✅ Reply to a user with <code>/approve</code> to approve them.", parse_mode=ParseMode.HTML)

        elif data == "cb_unapprove":
            await query.answer()
            await query.message.reply_text("🚫 Reply to a user with <code>/unapprove</code> to unapprove them.", parse_mode=ParseMode.HTML)

        else:
            await query.answer("Unknown command", show_alert=True)
