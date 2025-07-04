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

from utils.perms import is_admin
from utils.errors import catch_errors
from utils.db import set_setting, get_setting
from config import SUPPORT_CHAT_URL, DEVELOPER_URL

PANEL_IMAGE_URL = os.getenv("PANEL_IMAGE_URL", "https://files.catbox.moe/uvqeln.jpg")
DEFAULT_AUTODELETE_SECONDS = 60

def get_help_keyboard():
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

    # Send welcome panel for /start, /help, /menu
    @app.on_message(filters.command(["start", "help", "menu"]))
    async def show_panel(client: Client, message: Message):
        bot_user = await client.get_me()
        who = (
            message.chat.title
            if message.chat.type in ("group", "supergroup")
            else message.from_user.first_name
        )
        await message.reply_photo(
            photo=PANEL_IMAGE_URL,
            caption=(
                f"🎉 <b>Welcome to {who}</b>\n\n"
                f"I'm <b>{bot_user.first_name}</b>, here to help manage your group efficiently.\n"
                "You can tap the buttons below to explore available features.\n\n"
                "✅ Works in groups\n"
                "🛠 Admin-only settings\n"
                "🧠 Smart automation tools"
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📚 Help", callback_data="open_help_panel")]
            ]),
            parse_mode=ParseMode.HTML
        )

    # Send welcome automatically when bot is added to a group
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
                        "✅ Works in groups\n"
                        "🛠 Admin-only settings\n"
                        "🧠 Smart automation tools"
                    ),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("📚 Help", callback_data="open_help_panel")]
                    ]),
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                print(f"Error sending welcome panel: {e}")

    # Handle all help tab buttons
    @app.on_callback_query()
    async def help_panel_handler(client: Client, cb: CallbackQuery):
        data = cb.data

        if data == "open_help_panel":
            await cb.message.edit_caption(
                caption=(
                    "📚 <b>Bot Command Help</b>\n\n"
                    "Here you'll find details for all available plugins and features.\n\n"
                    "👇 Tap the buttons below to view help for each module:"
                ),
                reply_markup=get_help_keyboard(),
                parse_mode=ParseMode.HTML
            )
            return await cb.answer()

        elif data == "help_biomode":
            await cb.message.edit_caption(
                caption=(
                    "🛡 <b>BioMode</b>\n\n"
                    "Monitors user bios and deletes messages if they contain URLs.\n\n"
                    "<b>Usage:</b>\n"
                    "➤ <code>/biolink on</code> – Enable\n"
                    "➤ <code>/biolink off</code> – Disable\n\n"
                    "🚫 Blocks users with links in bio from messaging.\n"
                    "👮 Admins only."
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="open_help_panel")]
                ]),
                parse_mode=ParseMode.HTML
            )
            return await cb.answer()

        elif data == "help_autodelete":
            await cb.message.edit_caption(
                caption=(
                    "🧹 <b>AutoDelete</b>\n\n"
                    "Deletes messages after a delay.\n\n"
                    "<b>Usage:</b>\n"
                    "➤ <code>/autodelete 60</code>\n"
                    "➤ <code>/autodeleteon</code>\n"
                    "➤ <code>/autodeleteoff</code>\n\n"
                    "🧼 Helps keep the chat clean."
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="open_help_panel")]
                ]),
                parse_mode=ParseMode.HTML
            )
            return await cb.answer()

        elif data == "help_linkfilter":
            await cb.message.edit_caption(
                caption=(
                    "🔗 <b>LinkFilter</b>\n\n"
                    "Blocks messages with links from non-admins.\n\n"
                    "<b>Usage:</b>\n"
                    "➤ <code>/linkfilter on</code>\n"
                    "➤ <code>/linkfilter off</code>\n\n"
                    "🔒 Stops spam & scam links."
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="open_help_panel")]
                ]),
                parse_mode=ParseMode.HTML
            )
            return await cb.answer()

        elif data == "help_editmode":
            await cb.message.edit_caption(
                caption=(
                    "✏️ <b>EditMode</b>\n\n"
                    "Deletes edited messages instantly.\n\n"
                    "<b>Usage:</b>\n"
                    "➤ <code>/editmode on</code>\n"
                    "➤ <code>/editmode off</code>\n\n"
                    "🔍 Prevents stealth spam edits."
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="open_help_panel")]
                ]),
                parse_mode=ParseMode.HTML
            )
            return await cb.answer()

        elif data == "help_support":
            await cb.message.edit_caption(
                caption="🆘 <b>Need help?</b>\n\nJoin our support group for assistance and community help.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔗 Join Support", url=SUPPORT_CHAT_URL)],
                    [InlineKeyboardButton("🔙 Back", callback_data="open_help_panel")]
                ]),
                parse_mode=ParseMode.HTML
            )
            return await cb.answer()

        elif data == "help_developer":
            await cb.message.edit_caption(
                caption="👨‍💻 <b>Developer Info</b>\n\nGot feedback or questions? Contact the developer directly.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✉️ Message Developer", url=DEVELOPER_URL)],
                    [InlineKeyboardButton("🔙 Back", callback_data="open_help_panel")]
                ]),
                parse_mode=ParseMode.HTML
            )
            return await cb.answer()

    # ================== ADMIN COMMANDS ===================

    @app.on_message(filters.command("biolink") & filters.group)
    @catch_errors
    async def cmd_biolink(client: Client, message: Message):
        if not await is_admin(client, message): return
        args = message.text.split()
        if len(args) < 2 or args[1] not in {"on", "off"}:
            return await message.reply("Usage: /biolink on | off", parse_mode=ParseMode.HTML)
        await set_setting(message.chat.id, "biolink", "1" if args[1] == "on" else "0")
        await message.reply(f"BioMode {'enabled ✅' if args[1] == 'on' else 'disabled ❌'}", parse_mode=ParseMode.HTML)

    @app.on_message(filters.command("editmode") & filters.group)
    @catch_errors
    async def cmd_editmode(client: Client, message: Message):
        if not await is_admin(client, message): return
        args = message.text.split()
        if len(args) < 2 or args[1] not in {"on", "off"}:
            return await message.reply("Usage: /editmode on | off", parse_mode=ParseMode.HTML)
        await set_setting(message.chat.id, "editmode", "1" if args[1] == "on" else "0")
        await message.reply(f"EditMode {'enabled ✅' if args[1] == 'on' else 'disabled ❌'}", parse_mode=ParseMode.HTML)

    @app.on_message(filters.command("linkfilter") & filters.group)
    @catch_errors
    async def cmd_linkfilter(client: Client, message: Message):
        if not await is_admin(client, message): return
        args = message.text.split()
        if len(args) < 2 or args[1] not in {"on", "off"}:
            return await message.reply("Usage: /linkfilter on | off", parse_mode=ParseMode.HTML)
        await set_setting(message.chat.id, "linkfilter", "1" if args[1] == "on" else "0")
        await message.reply(f"LinkFilter {'enabled ✅' if args[1] == 'on' else 'disabled ❌'}", parse_mode=ParseMode.HTML)

    @app.on_message(filters.command(["autodelete", "setautodelete"]) & filters.group)
    @catch_errors
    async def cmd_autodelete(client: Client, message: Message):
        if not await is_admin(client, message): return
        if len(message.command) == 1:
            status = await get_setting(message.chat.id, "autodelete", "0")
            interval = await get_setting(message.chat.id, "autodelete_interval", "60")
            return await message.reply(f"🧹 AutoDelete: {interval}s ({'ON ✅' if status == '1' else 'OFF ❌'})", parse_mode=ParseMode.HTML)
        try:
            seconds = int(message.command[1])
            if seconds <= 0:
                raise ValueError
        except:
            return await message.reply("Usage: /autodelete <seconds>", parse_mode=ParseMode.HTML)
        await set_setting(message.chat.id, "autodelete", "1")
        await set_setting(message.chat.id, "autodelete_interval", str(seconds))
        await message.reply(f"🧹 AutoDelete set to {seconds}s ✅", parse_mode=ParseMode.HTML)

    @app.on_message(filters.command("autodeleteon") & filters.group)
    @catch_errors
    async def cmd_autodel_on(client: Client, message: Message):
        if not await is_admin(client, message): return
        await set_setting(message.chat.id, "autodelete", "1")
        await set_setting(message.chat.id, "autodelete_interval", str(DEFAULT_AUTODELETE_SECONDS))
        await message.reply(f"✅ AutoDelete enabled ({DEFAULT_AUTODELETE_SECONDS}s)", parse_mode=ParseMode.HTML)

    @app.on_message(filters.command("autodeleteoff") & filters.group)
    @catch_errors
    async def cmd_autodel_off(client: Client, message: Message):
        if not await is_admin(client, message): return
        await set_setting(message.chat.id, "autodelete", "0")
        await set_setting(message.chat.id, "autodelete_interval", "0")
        await message.reply("❌ AutoDelete disabled.", parse_mode=ParseMode.HTML)
