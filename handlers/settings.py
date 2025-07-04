import logging
import os
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from utils.perms import is_admin
from utils.errors import catch_errors
from utils.db import toggle_setting, get_setting, set_setting
from config import SUPPORT_CHAT_URL, DEVELOPER_URL  # Make sure these exist

logger = logging.getLogger(__name__)
DEFAULT_AUTODELETE_SECONDS = 60
PANEL_IMAGE_URL = os.getenv("PANEL_IMAGE_URL", "https://files.catbox.moe/uvqeln.jpg")


async def build_start_panel(is_admin: bool) -> InlineKeyboardMarkup:
    """Return the inline keyboard for the /start screen."""
    buttons = [[InlineKeyboardButton("📚 Commands", callback_data="cb_help_start")]]
    if is_admin:
        buttons.append([InlineKeyboardButton("⚙️ Settings", callback_data="cb_open_panel")])
    return InlineKeyboardMarkup(buttons)


async def build_group_panel(chat_id: int, client: Client) -> tuple[str, InlineKeyboardMarkup]:
    """Return caption and keyboard showing current group settings."""
    biolink = await get_setting(chat_id, "biolink", "0")
    autodel = await get_setting(chat_id, "autodelete", "0")
    interval = await get_setting(chat_id, "autodelete_interval", "60")
    linkfilter = await get_setting(chat_id, "linkfilter", "0")
    editmode = await get_setting(chat_id, "editmode", "0")

    caption = (
        "<b>Current Settings</b>\n"
        f"Bio Filter: {'ON ✅' if biolink == '1' else 'OFF ❌'}\n"
        f"Auto-Delete: {'ON ✅ (' + interval + 's)' if autodel == '1' else 'OFF ❌'}\n"
        f"Link Filter: {'ON ✅' if linkfilter == '1' else 'OFF ❌'}\n"
        f"Edit Mode: {'ON ✅' if editmode == '1' else 'OFF ❌'}"
    )

    keyboard = [
        [InlineKeyboardButton(f"Bio Filter {'✅' if biolink == '1' else '❌'}", callback_data="cb_toggle_biolink")],
        [InlineKeyboardButton(f"AutoDelete {'✅' if autodel == '1' else '❌'}", callback_data="cb_toggle_autodel")],
        [InlineKeyboardButton(f"Link Filter {'✅' if linkfilter == '1' else '❌'}", callback_data="cb_toggle_linkfilter")],
        [InlineKeyboardButton(f"Edit Mode {'✅' if editmode == '1' else '❌'}", callback_data="cb_toggle_editmode")],
        [InlineKeyboardButton("✅ Approve", callback_data="cb_approve"), InlineKeyboardButton("❌ Unapprove", callback_data="cb_unapprove")],
        [InlineKeyboardButton("◀️ Back", callback_data="cb_back_panel")],
    ]
    return caption, InlineKeyboardMarkup(keyboard)


async def send_start(client: Client, message: Message) -> None:
    markup = await build_start_panel(await is_admin(client, message))
    await message.reply_text("Choose an option:", reply_markup=markup)


async def send_control_panel(client: Client, message: Message) -> None:
    caption, markup = await build_group_panel(message.chat.id, client)
    await message.reply_text(caption, reply_markup=markup, parse_mode=ParseMode.HTML)

def get_panel_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛡️ BioMode", callback_data="panel_biomode")],
        [InlineKeyboardButton("🧹 AutoDelete", callback_data="panel_autodelete")],
        [InlineKeyboardButton("🔗 LinkFilter", callback_data="panel_linkfilter")],
        [InlineKeyboardButton("✏️ EditMode", callback_data="panel_editmode")],
        [
            InlineKeyboardButton("👨‍💻 Developer", callback_data="panel_developer"),
            InlineKeyboardButton("🆘 Support", callback_data="panel_support")
        ]
    ])

def register(app: Client) -> None:
    # /start command (for private or group)
    @app.on_message(filters.command("start"))
    async def cmd_start(client: Client, message: Message):
        await client.send_photo(
            chat_id=message.chat.id,
            photo=PANEL_IMAGE_URL,
            caption=(
                "🎉 <b>Welcome to Sirion Bot</b>\n\n"
                "I'm here to help manage your group efficiently.\n"
                "You can tap the buttons below to explore available features.\n\n"
                "✅ Works in groups\n🛠 Admin-only settings\n🧠 Smart automation tools"
            ),
            reply_markup=get_panel_keyboard(),
            parse_mode=ParseMode.HTML
        )

    # /menu command (admin-only in groups)
    @app.on_message(filters.command("menu") & filters.group)
    async def cmd_menu(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text("🔒 <b>Admins only.</b>", parse_mode=ParseMode.HTML)
            return

        await client.send_photo(
            chat_id=message.chat.id,
            photo=PANEL_IMAGE_URL,
            caption=(
                "📚 <b>Bot Command Help</b>\n\n"
                "Here you'll find details for all available plugins and features.\n\n"
                "👇 Tap the buttons below to view help for each module:"
            ),
            reply_markup=get_panel_keyboard(),
            parse_mode=ParseMode.HTML
        )

    # /help command (anywhere)
    @app.on_message(filters.command("help"))
    async def cmd_help(client: Client, message: Message):
        await message.reply_text(
            "📌 <b>Available Modules</b>\n\n"
            "➤ BioMode\n"
            "➤ AutoDelete\n"
            "➤ LinkFilter\n"
            "➤ EditMode\n\n"
            "Use <code>/menu</code> in group or <code>/start</code> here to open full panel.",
            parse_mode=ParseMode.HTML,
            reply_markup=get_panel_keyboard()
        )

    # Callback query handler
    @app.on_callback_query()
    async def panel_navigation(client, cb):
        panels = {
            "panel_biomode": {
                "caption": (
                    "🛡 <b>BioMode</b>\n\n"
                    "Monitors user bios and deletes messages if they contain URLs.\n\n"
                    "<b>Usage:</b>\n"
                    "➤ <code>/biolink on</code>\n"
                    "➤ <code>/biolink off</code>\n\n"
                    "🚫 Blocks messages from users with links in bios.\n"
                    "👮 Admins only."
                )
            },
            "panel_autodelete": {
                "caption": (
                    "🧹 <b>AutoDelete</b>\n\n"
                    "Deletes messages after a delay.\n\n"
                    "<b>Usage:</b>\n"
                    "➤ <code>/autodelete 60</code>\n"
                    "➤ <code>/autodeleteon</code>\n"
                    "➤ <code>/autodeleteoff</code>\n\n"
                    "🕒 Automatically removes messages."
                )
            },
            "panel_linkfilter": {
                "caption": (
                    "🔗 <b>LinkFilter</b>\n\n"
                    "Blocks messages with links from non-admins.\n\n"
                    "<b>Usage:</b>\n"
                    "➤ <code>/linkfilter on</code>\n"
                    "➤ <code>/linkfilter off</code>\n\n"
                    "🔒 Keeps spam out."
                )
            },
            "panel_editmode": {
                "caption": (
                    "✏️ <b>EditMode</b>\n\n"
                    "Deletes edited messages automatically.\n\n"
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
            await cb.message.edit_caption(
                caption="📚 <b>Bot Command Help</b>\n\n"
                        "Here you'll find details for all available plugins and features.\n\n"
                        "👇 Tap the buttons below to view help for each module:",
                parse_mode=ParseMode.HTML,
                reply_markup=get_panel_keyboard()
            )
            await cb.answer()

        elif cb.data == "panel_support":
            await cb.answer("🆘 Join our support group:\n" + SUPPORT_CHAT_URL, show_alert=True)

        elif cb.data == "panel_developer":
            await cb.answer("👨‍💻 Contact the developer here:\n" + DEVELOPER_URL, show_alert=True)

    # Admin command handlers
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
        else:
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
        state = await toggle_setting(message.chat.id, "linkfilter")
        await message.reply_text(
            f"🔗 Link filter {'enabled ✅' if state == '1' else 'disabled ❌'}",
            parse_mode=ParseMode.HTML,
        )
