import logging
import os
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton
)

from utils.perms import is_admin
from utils.errors import catch_errors
from utils.db import toggle_setting, get_setting, set_setting

logger = logging.getLogger(__name__)
DEFAULT_AUTODELETE_SECONDS = 60
PANEL_IMAGE_URL = os.getenv("PANEL_IMAGE_URL", "https://files.catbox.moe/uvqeln.jpg")


def register(app: Client) -> None:

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

    @app.on_message(filters.command("autodeleteoff") & filters.group)
    @catch_errors
    async def disable_autodel(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text("🔒 <b>Admins only.</b>", parse_mode=ParseMode.HTML)
            return
        await set_setting(message.chat.id, "autodelete", "0")
        await set_setting(message.chat.id, "autodelete_interval", "0")
        await message.reply_text("🧹 Auto-delete disabled.", parse_mode=ParseMode.HTML)

    @app.on_message(filters.command("linkfilter") & filters.group)
    @catch_errors
    async def cmd_linkfilter(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text("🔒 <b>Admins only.</b>", parse_mode=ParseMode.HTML)
            return
        arg = message.command[1].lower() if len(message.command) > 1 else None
        if arg in {"on", "off"}:
            state = "1" if arg == "on" else "0"
            await set_setting(message.chat.id, "linkfilter", state)
        else:
            state = await toggle_setting(message.chat.id, "linkfilter")
        await message.reply_text(
            f"🔗 Link filter {'enabled ✅' if state == '1' else 'disabled ❌'}",
            parse_mode=ParseMode.HTML,
        )

    @app.on_message(filters.command("autodeleteedited") & filters.group)
    @catch_errors
    async def cmd_autodeleteedited(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text("🔒 <b>Admins only.</b>", parse_mode=ParseMode.HTML)
            return
        arg = message.command[1].lower() if len(message.command) > 1 else None
        if arg in {"on", "off"}:
            state = "1" if arg == "on" else "0"
            await set_setting(message.chat.id, "editmode", state)
        else:
            state = await toggle_setting(message.chat.id, "editmode")
        await message.reply_text(
            f"📝 Edited delete {'enabled ✅' if state == '1' else 'disabled ❌'}",
            parse_mode=ParseMode.HTML,
        )

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
                "🤖 <b>Bot Control Panel</b>\n\n"
                "Use the buttons below to view and manage your bot settings:"
            ),
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )

    @app.on_message(filters.new_chat_members)
    async def bot_added_to_group(client: Client, message: Message):
        for member in message.new_chat_members:
            if member.id == client.me.id:
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
                        "👋 <b>Hello! I'm ready to protect this group.</b>\n\n"
                        "Here’s your control panel to configure moderation features 👇"
                    ),
                    reply_markup=keyboard,
                    parse_mode=ParseMode.HTML
                )
                break

    @app.on_callback_query()
    async def panel_navigation(client, cb):
        descriptions = {
            "panel_biomode": (
                "🛡️ <b>BioMode</b>\n\n"
                "Monitors bios & blocks users with links from messaging.\n\n"
                "<b>Commands:</b>\n"
                "• <code>/biolink on</code> – Enable\n"
                "• <code>/biolink off</code> – Disable\n\n"
                "👮 Admins only."
            ),
            "panel_autodelete": (
                "🧹 <b>AutoDelete</b>\n\n"
                "Deletes messages automatically after a set interval.\n\n"
                "<b>Commands:</b>\n"
                "• <code>/autodelete 60</code>\n"
                "• <code>/autodeleteon</code>\n"
                "• <code>/autodeleteoff</code>\n\n"
                "🕒 Default: 60s"
            ),
            "panel_linkfilter": (
                "🔗 <b>LinkFilter</b>\n\n"
                "Blocks messages containing links from non-admins.\n\n"
                "<b>Commands:</b>\n"
                "• <code>/linkfilter on</code>\n"
                "• <code>/linkfilter off</code>\n\n"
                "👮 Admins only."
            ),
            "panel_editmode": (
                "✏️ <b>EditMode</b>\n\n"
                "Deletes messages after they're edited, if enabled.\n\n"
                "<b>Commands:</b>\n"
                "• <code>/editmode on</code>\n"
                "• <code>/editmode off</code>\n\n"
                "👮 Admins only."
            ),
        }

        if cb.data in descriptions:
            await cb.message.edit_caption(
                caption=descriptions[cb.data],
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="panel_back")]
                ]),
                parse_mode=ParseMode.HTML
            )
        elif cb.data == "panel_back":
            await cb.message.edit_caption(
                caption=(
                    "🤖 <b>Bot Control Panel</b>\n\n"
                    "Use the buttons below to view and manage your bot settings:"
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🛡️ BioMode", callback_data="panel_biomode")],
                    [InlineKeyboardButton("🧹 AutoDelete", callback_data="panel_autodelete")],
                    [InlineKeyboardButton("🔗 LinkFilter", callback_data="panel_linkfilter")],
                    [InlineKeyboardButton("✏️ EditMode", callback_data="panel_editmode")]
                ]),
                parse_mode=ParseMode.HTML
            )
        await cb.answer()
