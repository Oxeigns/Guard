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
    # Get shared control panel markup and caption
    def get_control_panel():
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛡️ BioMode", callback_data="panel_biomode")],
            [InlineKeyboardButton("🧹 AutoDelete", callback_data="panel_autodelete")],
            [InlineKeyboardButton("🔗 LinkFilter", callback_data="panel_linkfilter")],
            [InlineKeyboardButton("✏️ EditMode", callback_data="panel_editmode")]
        ])
        caption = (
            "📚 <b>Bot Command Help</b>\n\n"
            "Here you'll find details for all available plugins and features.\n\n"
            "👇 Tap the buttons below to view help for each module:"
        )
        return keyboard, caption

    # Show control panel on /start or /menu
    @app.on_message(filters.command(["start", "menu"]) & filters.group)
    async def show_control_panel(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text("🔒 <b>Admins only.</b>", parse_mode=ParseMode.HTML)
            return

        keyboard, caption = get_control_panel()

        await client.send_photo(
            chat_id=message.chat.id,
            photo=PANEL_IMAGE_URL,
            caption=caption,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )

    # Panel callback navigation
    @app.on_callback_query()
    async def panel_navigation(client, cb):
        panels = {
            "panel_biomode": {
                "caption": (
                    "🛡 <b>BioMode</b> monitors user bios and deletes messages if they contain URLs.\n\n"
                    "<b>Usage:</b>\n"
                    "➤ <code>/biolink on</code>\n"
                    "➤ <code>/biolink off</code>\n\n"
                    "🚫 Blocks messages from users with links in bios.\n"
                    "👮 Admins only."
                )
            },
            "panel_autodelete": {
                "caption": (
                    "🧹 <b>AutoDelete</b> deletes messages after a time delay.\n\n"
                    "<b>Usage:</b>\n"
                    "➤ <code>/autodelete 60</code>\n"
                    "➤ <code>/autodeleteon</code>\n"
                    "➤ <code>/autodeleteoff</code>\n\n"
                    "🕒 Automatically removes messages."
                )
            },
            "panel_linkfilter": {
                "caption": (
                    "🔗 <b>LinkFilter</b> blocks messages with links from non-admins.\n\n"
                    "<b>Usage:</b>\n"
                    "➤ <code>/linkfilter on</code>\n"
                    "➤ <code>/linkfilter off</code>\n\n"
                    "🔒 Keeps spam out."
                )
            },
            "panel_editmode": {
                "caption": (
                    "✏️ <b>EditMode</b> deletes edited messages automatically.\n\n"
                    "<b>Usage:</b>\n"
                    "➤ <code>/editmode on</code>\n"
                    "➤ <code>/editmode off</code>\n\n"
                    "🕵️ Prevents sneaky edits."
                )
            }
        }

        if cb.data in panels:
            await cb.message.edit_caption(
                caption=panels[cb.data]["caption"],
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="panel_back")]
                ])
            )
            await cb.answer()
        elif cb.data == "panel_back":
            keyboard, caption = get_control_panel()
            await cb.message.edit_caption(
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
            )
            await cb.answer()

    # Admin command: /biolink
    @app.on_message(filters.command("biolink") & filters.group)
    @catch_errors
    async def cmd_biolink(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text("🔒 <b>Admins only.</b>", parse_mode=ParseMode.HTML)
            return
        state = await toggle_setting(message.chat.id, "biolink")
        await message.reply_text(
            f"🔗 Bio filter {'enabled ✅' if state == '1' else 'disabled ❌'}",
            parse_mode=ParseMode.HTML,
        )

    # Admin command: /editmode
    @app.on_message(filters.command("editmode") & filters.group)
    @catch_errors
    async def cmd_editmode(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text("🔒 <b>Admins only.</b>", parse_mode=ParseMode.HTML)
            return
        state = await toggle_setting(message.chat.id, "editmode")
        await message.reply_text(
            f"✏️ Edit mode {'enabled ✅' if state == '1' else 'disabled ❌'}",
            parse_mode=ParseMode.HTML,
        )

    # Admin command: /autodelete or /setautodelete
    @app.on_message(filters.command(["autodelete", "setautodelete"]) & filters.group)
    @catch_errors
    async def cmd_autodelete(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text("🔒 <b>Admins only.</b>", parse_mode=ParseMode.HTML)
            return
        if len(message.command) == 1:
            current = await get_setting(message.chat.id, "autodelete", "0")
            interval = await get_setting(message.chat.id, "autodelete_interval", "0")
            await message.reply_text(
                f"🕒 Auto-delete: <code>{interval}s</code> ({'on' if current=='1' else 'off'})",
                parse_mode=ParseMode.HTML,
            )
            return
        try:
            seconds = int(message.command[1])
            if seconds <= 0:
                raise ValueError
        except ValueError:
            await message.reply_text("⚠️ Usage: /autodelete <seconds>", parse_mode=ParseMode.HTML)
            return
        await set_setting(message.chat.id, "autodelete", "1")
        await set_setting(message.chat.id, "autodelete_interval", str(seconds))
        await message.reply_text(
            f"🧹 Auto-delete set to <b>{seconds}</b> seconds",
            parse_mode=ParseMode.HTML,
        )

    # Admin command: /autodeleteon
    @app.on_message(filters.command("autodeleteon") & filters.group)
    @catch_errors
    async def enable_autodel(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text("🔒 <b>Admins only.</b>", parse_mode=ParseMode.HTML)
            return
        await set_setting(message.chat.id, "autodelete", "1")
        await set_setting(message.chat.id, "autodelete_interval", str(DEFAULT_AUTODELETE_SECONDS))
        await message.reply_text(
            f"✅ Auto-delete enabled: <code>{DEFAULT_AUTODELETE_SECONDS}s</code>",
            parse_mode=ParseMode.HTML,
        )

    # Admin command: /autodeleteoff
    @app.on_message(filters.command("autodeleteoff") & filters.group)
    @catch_errors
    async def disable_autodel(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text("🔒 <b>Admins only.</b>", parse_mode=ParseMode.HTML)
            return
        await set_setting(message.chat.id, "autodelete", "0")
        await set_setting(message.chat.id, "autodelete_interval", "0")
        await message.reply_text("🧹 Auto-delete disabled.", parse_mode=ParseMode.HTML)

    # Admin command: /linkfilter
    @app.on_message(filters.command("linkfilter") & filters.group)
    @catch_errors
    async def cmd_linkfilter(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text("🔒 <b>Admins only.</b>", parse_mode=ParseMode.HTML)
            return
        state = await toggle_setting(message.chat.id, "linkfilter")
        await message.reply_text(
            f"🔗 Link filter {'enabled ✅' if state == '1' else 'disabled ❌'}",
            parse_mode=ParseMode.HTML,
        )
