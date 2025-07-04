import os
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton
)

HELP_IMAGE_URL = os.getenv("PANEL_IMAGE_URL", "https://files.catbox.moe/uvqeln.jpg")

def register_help_ui(app: Client) -> None:

    @app.on_message(filters.command("help") & filters.group)
    async def show_help_panel(client: Client, message: Message):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛡️ BioMode", callback_data="help_biomode")],
            [InlineKeyboardButton("📝 Long Message", callback_data="help_long")],
            [InlineKeyboardButton("🔗 LinkFilter", callback_data="help_linkfilter")],
            [InlineKeyboardButton("🔙 Back", callback_data="help_back")],
        ])

        await client.send_photo(
            chat_id=message.chat.id,
            photo=HELP_IMAGE_URL,
            caption=(
                "📚 <b>Bot Command Help</b>\n\n"
                "Here you'll find details for all available plugins and features.\n\n"
                "👇 Tap the buttons below to view help for each module:"
            ),
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )

    @app.on_callback_query()
    async def help_callback_handler(client: Client, cb):
        help_data = {
            "help_biomode": (
                "🛡️ <b>BioMode</b>\n\n"
                "<i>Blocks users with URLs in their bio from sending messages.</i>\n\n"
                "<b>Commands:</b>\n"
                "• <code>/biolink on</code>\n"
                "• <code>/biolink off</code>\n\n"
                "👮 Admin-only setting."
            ),
            "help_long": (
                "📝 <b>Long Message Filter</b>\n\n"
                "<i>Auto-deletes messages longer than a set limit.</i>\n\n"
                "<b>Usage:</b>\n"
                "• <code>/setlonglimit 800</code> (Range: 200–4000)\n"
                "Default: 800 characters"
            ),
            "help_linkfilter": (
                "🔗 <b>Link Filter</b>\n\n"
                "<i>Removes any links sent by non-admins in the group.</i>\n\n"
                "<b>Commands:</b>\n"
                "• <code>/linkfilter on</code>\n"
                "• <code>/linkfilter off</code>\n"
                "👮 Admin-only setting."
            ),
        }

        if cb.data in help_data:
            await cb.message.edit_caption(
                caption=help_data[cb.data],
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="help_back")]
                ]),
                parse_mode=ParseMode.HTML
            )

        elif cb.data == "help_back":
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🛡️ BioMode", callback_data="help_biomode")],
                [InlineKeyboardButton("📝 Long Message", callback_data="help_long")],
                [InlineKeyboardButton("🔗 LinkFilter", callback_data="help_linkfilter")],
                [InlineKeyboardButton("🔙 Back", callback_data="help_back")],
            ])
            await cb.message.edit_caption(
                caption=(
                    "📚 <b>Bot Command Help</b>\n\n"
                    "Here you'll find details for all available plugins and features.\n\n"
                    "👇 Tap the buttons below to view help for each module:"
                ),
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )

        await cb.answer()
