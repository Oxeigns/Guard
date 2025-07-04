import logging
import os
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from utils.perms import is_admin
from utils.errors import catch_errors
from utils.db import toggle_setting, get_setting, set_setting

logger = logging.getLogger(__name__)
DEFAULT_AUTODELETE_SECONDS = 60
PANEL_IMAGE_URL = os.getenv("PANEL_IMAGE_URL", "https://files.catbox.moe/uvqeln.jpg")


def register(app: Client) -> None:
    @app.on_message(filters.command("panel") & filters.group)
    async def control_panel(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text("🔒 <b>Admins only.</b>", parse_mode=ParseMode.HTML)
            return

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛡️ BioMode", callback_data="panel_biomode")],
            [InlineKeyboardButton("🧹 AutoDelete", callback_data="panel_autodelete")],
            [InlineKeyboardButton("🔗 LinkFilter", callback_data="panel_linkfilter")],
            [InlineKeyboardButton("✏️ EditMode", callback_data="panel_editmode")]
        ])

        await client.send_photo(
            chat_id=message.chat.id,
            photo=PANEL_IMAGE_URL,
            caption=(
                "📚 <b>Bot Command Help</b>\n\n"
                "Here you'll find details for all available plugins and features.\n\n"
                "👇 Tap the buttons below to view help for each module:"
            ),
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )

    @app.on_callback_query()
    async def panel_navigation(client, cb):
        panels = {
            "panel_biomode": {
                "title": "🛡 BioMode",
                "caption": (
                    "🛡 <b>BioMode</b> monitors user bios and deletes messages if they contain URLs.\n\n"
                    "<b>Usage:</b>\n"
                    "➤ <code>/biolink on</code> – Enable BioMode\n"
                    "➤ <code>/biolink off</code> – Disable BioMode\n\n"
                    "🚫 When enabled, users with links in their bios won't be able to send messages.\n"
                    "👮 Only admins can enable or disable this feature."
                )
            },
            "panel_autodelete": {
                "title": "🧹 AutoDelete",
                "caption": (
                    "🧹 <b>AutoDelete</b> deletes messages after a time delay.\n\n"
                    "<b>Usage:</b>\n"
                    "➤ <code>/autodelete 60</code> – Set to 60s\n"
                    "➤ <code>/autodeleteon</code> – Enable (60s default)\n"
                    "➤ <code>/autodeleteoff</code> – Disable\n\n"
                    "🕒 Messages will be removed automatically after this interval."
                )
            },
            "panel_linkfilter": {
                "title": "🔗 LinkFilter",
                "caption": (
                    "🔗 <b>LinkFilter</b> prevents non-admins from sending messages with links.\n\n"
                    "<b>Usage:</b>\n"
                    "➤ <code>/linkfilter on</code>\n"
                    "➤ <code>/linkfilter off</code>\n\n"
                    "🔒 Keeps spam links out of your group."
                )
            },
            "panel_editmode": {
                "title": "✏️ EditMode",
                "caption": (
                    "✏️ <b>EditMode</b> automatically deletes edited messages.\n\n"
                    "<b>Usage:</b>\n"
                    "➤ <code>/editmode on</code>\n"
                    "➤ <code>/editmode off</code>\n\n"
                    "👮 Prevents sneaky edits from bypassing filters."
                )
            }
        }

        if cb.data in panels:
            content = panels[cb.data]
            await cb.message.edit_caption(
                caption=content["caption"],
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="panel_back")]
                ])
            )
            await cb.answer()

        elif cb.data == "panel_back":
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🛡️ BioMode", callback_data="panel_biomode")],
                [InlineKeyboardButton("🧹 AutoDelete", callback_data="panel_autodelete")],
                [InlineKeyboardButton("🔗 LinkFilter", callback_data="panel_linkfilter")],
                [InlineKeyboardButton("✏️ EditMode", callback_data="panel_editmode")]
            ])

            await cb.message.edit_caption(
                caption=(
                    "📚 <b>Bot Command Help</b>\n\n"
                    "Here you'll find details for all available plugins and features.\n\n"
                    "👇 Tap the buttons below to view help for each module:"
                ),
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
            )
            await cb.answer()
