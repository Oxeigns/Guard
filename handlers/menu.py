import logging
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery

from config import SUPPORT_CHAT_URL, DEVELOPER_URL
from utils.errors import catch_errors
from utils.storage import get_bio_filter, set_bio_filter
from utils.perms import is_admin

logger = logging.getLogger(__name__)


def elid(text: str, max_len: int = 20) -> str:
    """Return text truncated to ``max_len`` characters with an ellipsis."""
    return text if len(text) <= max_len else text[: max_len - 1] + "…"


async def build_panel(chat_id: int) -> tuple[str, InlineKeyboardMarkup]:
    status = await get_bio_filter(chat_id)
    caption = f"🛡 Bio Filter: {'ON' if status else 'OFF'}"
    buttons = [
        [InlineKeyboardButton(elid("📖 Help & Commands"), callback_data="help")],
        [
            InlineKeyboardButton(elid("📣 Support Channel"), url=SUPPORT_CHAT_URL),
            InlineKeyboardButton(elid("👨‍💻 Developer"), url=DEVELOPER_URL),
        ],
        [
            InlineKeyboardButton(elid("⚪ Turn On"), callback_data="biolink_on"),
            InlineKeyboardButton(elid("🔴 Turn Off"), callback_data="biolink_off"),
        ],
    ]
    return caption, InlineKeyboardMarkup(buttons)


async def send_panel(client: Client, message: Message) -> None:
    caption, markup = await build_panel(message.chat.id)
    await message.reply_text(caption, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)


async def edit_panel(query: CallbackQuery) -> None:
    caption, markup = await build_panel(query.message.chat.id)
    await query.message.edit_text(caption, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)


def register(app: Client) -> None:
    @app.on_message(filters.command(["start", "menu"]))
    @catch_errors
    async def start_menu(client: Client, message: Message):
        logger.info("%s in %s", message.command[0], message.chat.id)
        if message.chat.type != "private" and not await is_admin(client, message):
            await message.reply_text("❌ You must be an admin to use this command.")
            return
        await send_panel(client, message)

    @app.on_callback_query(filters.regex(r"^help$"))
    @catch_errors
    async def help_cb(client: Client, query: CallbackQuery):
        logger.info("help callback from %s", query.from_user.id)
        help_text = (
            "*Commands:*\n"
            "/approve - approve user\n"
            "/unapprove - unapprove user\n"
            "/viewapproved - list approved\n"
            "/setautodelete <sec> - auto delete\n"
            "/mute - mute replied user\n"
            "/kick - kick replied user\n"
            "/biolink [on|off] - toggle bio filter\n"
        )
        markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(elid("◀️ Back"), callback_data="back_to_panel")]]
        )
        await query.message.edit_text(help_text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)

    @app.on_callback_query(filters.regex(r"^back_to_panel$"))
    @catch_errors
    async def back_cb(client: Client, query: CallbackQuery):
        await query.answer()
        await edit_panel(query)

    @app.on_callback_query(filters.regex(r"^biolink_on$"))
    @catch_errors
    async def biolink_on_cb(client: Client, query: CallbackQuery):
        await set_bio_filter(query.message.chat.id, True)
        await query.answer("Enabled")
        await edit_panel(query)

    @app.on_callback_query(filters.regex(r"^biolink_off$"))
    @catch_errors
    async def biolink_off_cb(client: Client, query: CallbackQuery):
        await set_bio_filter(query.message.chat.id, False)
        await query.answer("Disabled")
        await edit_panel(query)
