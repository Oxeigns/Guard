from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    ChatMemberUpdated,
)
import os
from html import escape

from utils.perms import is_admin
from config import SUPPORT_CHAT_URL, DEVELOPER_URL

PANEL_IMAGE_URL = os.getenv("PANEL_IMAGE_URL", "https://files.catbox.moe/uvqeln.jpg")


def mention_html(user_id: int, name: str) -> str:
    return f'<a href="tg://user?id={user_id}">{escape(name)}</a>'


async def build_start_panel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 Commands", callback_data="cb_help_start")]
    ])


async def send_start(client: Client, message: Message) -> None:
    bot_user = await client.get_me()
    user = message.from_user
    markup = await build_start_panel()

    await message.reply_photo(
        photo=PANEL_IMAGE_URL,
        caption=(
            f"🎉 <b>Welcome to {bot_user.first_name}</b>\n\n"
            f"Hello {mention_html(user.id, user.first_name)}!\n\n"
            "I'm here to help manage your group efficiently.\n"
            "You can tap the buttons below to explore available features.\n\n"
            "✅ Works in groups\n🛠 Admin-only settings\n🧠 Smart automation tools"
        ),
        reply_markup=markup,
        parse_mode=ParseMode.HTML,
    )


def get_help_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛡️ BioMode", callback_data="help_biomode")],
        [InlineKeyboardButton("🧹 AutoDelete", callback_data="help_autodelete")],
        [InlineKeyboardButton("🔗 LinkFilter", callback_data="help_linkfilter")],
        [InlineKeyboardButton("✏️ EditMode", callback_data="help_editmode")],
        [
            InlineKeyboardButton("👨‍💻 Developer", callback_data="help_developer"),
            InlineKeyboardButton("🆘 Support", callback_data="help_support")
        ]
    ])


def register(app: Client):
    # One panel for all command triggers
    @app.on_message(filters.command(["start", "help", "menu"]))
    async def show_start_panel(client: Client, message: Message):
        await send_start(client, message)

    # Show welcome panel automatically when added to a group
    @app.on_chat_member_updated()
    async def send_panel_on_add(client: Client, update: ChatMemberUpdated):
        if update.new_chat_member.user.is_self:
            bot_user = await client.get_me()
            try:
                await client.send_photo(
                    chat_id=update.chat.id,
                    photo=PANEL_IMAGE_URL,
                    caption=(
                        f"🎉 <b>Welcome to {update.chat.title}</b>\n\n"
                        f"I'm <b>{bot_user.first_name}</b>, here to help manage your group efficiently.\n"
                        "You can tap the buttons below to explore available features.\n\n"
                        "✅ Works in groups\n🛠 Admin-only settings\n🧠 Smart automation tools"
                    ),
                    reply_markup=await build_start_panel(),
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                print(f"Error sending welcome panel: {e}")

    # Handle command help panel (with fallback)
    @app.on_callback_query()
    async def help_panel_handler(client: Client, cb: CallbackQuery):
        data = cb.data

        if data == "cb_help_start":
            text = (
                "📚 <b>Bot Command Help</b>\n\n"
                "Here you'll find details for all available plugins and features.\n\n"
                "👇 Tap the buttons below to view help for each module:"
            )
            markup = get_help_keyboard()
            try:
                await cb.message.edit_caption(
                    caption=text,
                    reply_markup=markup,
                    parse_mode=ParseMode.HTML
                )
            except:
                await cb.message.edit_text(
                    text=text,
                    reply_markup=markup,
                    parse_mode=ParseMode.HTML
                )
            return await cb.answer()

        # -- Individual Help Sections --
        help_texts = {
            "help_biomode": (
                "🛡 <b>BioMode</b>\n\n"
                "Monitors user bios and deletes messages if they contain URLs.\n\n"
                "<b>Usage:</b>\n"
                "➤ <code>/biolink on</code>\n"
                "➤ <code>/biolink off</code>\n\n"
                "🚫 Blocks users with links in bio from messaging.\n"
                "👮 Admins only."
            ),
            "help_autodelete": (
                "🧹 <b>AutoDelete</b>\n\n"
                "Deletes messages after a delay.\n\n"
                "<b>Usage:</b>\n"
                "➤ <code>/autodelete 60</code>\n"
                "➤ <code>/autodeleteon</code>\n"
                "➤ <code>/autodeleteoff</code>\n\n"
                "🧼 Helps keep the chat clean."
            ),
            "help_linkfilter": (
                "🔗 <b>LinkFilter</b>\n\n"
                "Blocks messages with links from non-admins.\n\n"
                "<b>Usage:</b>\n"
                "➤ <code>/linkfilter on</code>\n"
                "➤ <code>/linkfilter off</code>\n\n"
                "🔒 Stops spam & scam links."
            ),
            "help_editmode": (
                "✏️ <b>EditMode</b>\n\n"
                "Deletes edited messages instantly.\n\n"
                "<b>Usage:</b>\n"
                "➤ <code>/editmode on</code>\n"
                "➤ <code>/editmode off</code>\n\n"
                "🔍 Prevents stealth spam edits."
            ),
        }

        if data in help_texts:
            try:
                await cb.message.edit_caption(
                    caption=help_texts[data],
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Back", callback_data="cb_help_start")]
                    ]),
                    parse_mode=ParseMode.HTML
                )
            except:
                await cb.message.edit_text(
                    text=help_texts[data],
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Back", callback_data="cb_help_start")]
                    ]),
                    parse_mode=ParseMode.HTML
                )
            return await cb.answer()

        if data == "help_support":
            try:
                await cb.message.edit_caption(
                    caption="🆘 <b>Need help?</b>\n\nJoin our support group for assistance and community help.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔗 Join Support", url=SUPPORT_CHAT_URL)],
                        [InlineKeyboardButton("🔙 Back", callback_data="cb_help_start")]
                    ]),
                    parse_mode=ParseMode.HTML
                )
            except:
                await cb.message.edit_text(
                    text="🆘 <b>Need help?</b>\n\nJoin our support group for assistance and community help.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔗 Join Support", url=SUPPORT_CHAT_URL)],
                        [InlineKeyboardButton("🔙 Back", callback_data="cb_help_start")]
                    ]),
                    parse_mode=ParseMode.HTML
                )
            return await cb.answer()

        if data == "help_developer":
            try:
                await cb.message.edit_caption(
                    caption="👨‍💻 <b>Developer Info</b>\n\nGot feedback or questions? Contact the developer directly.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("✉️ Message Developer", url=DEVELOPER_URL)],
                        [InlineKeyboardButton("🔙 Back", callback_data="cb_help_start")]
                    ]),
                    parse_mode=ParseMode.HTML
                )
            except:
                await cb.message.edit_text(
                    text="👨‍💻 <b>Developer Info</b>\n\nGot feedback or questions? Contact the developer directly.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("✉️ Message Developer", url=DEVELOPER_URL)],
                        [InlineKeyboardButton("🔙 Back", callback_data="cb_help_start")]
                    ]),
                    parse_mode=ParseMode.HTML
                )
            return await cb.answer()
