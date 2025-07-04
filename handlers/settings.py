import logging
import os
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from html import escape

from utils.perms import is_admin
from utils.errors import catch_errors
from utils.db import toggle_setting, get_setting, set_setting
from config import SUPPORT_CHAT_URL, DEVELOPER_URL

logger = logging.getLogger(__name__)
DEFAULT_AUTODELETE_SECONDS = 60
PANEL_IMAGE_URL = os.getenv("PANEL_IMAGE_URL", "https://files.catbox.moe/uvqeln.jpg")


def mention_html(user_id: int, name: str) -> str:
    """Return an HTML user mention string."""
    return f'<a href="tg://user?id={user_id}">{escape(name)}</a>'


# UI Components
def get_panel_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛡️ BioMode", callback_data="panel_biomode")],
        [InlineKeyboardButton("🧹 AutoDelete", callback_data="panel_autodelete")],
        [InlineKeyboardButton("🔗 LinkFilter", callback_data="panel_linkfilter")],
        [InlineKeyboardButton("✏️ EditMode", callback_data="panel_editmode")],
        [
            InlineKeyboardButton("👨‍💻 Developer", url=DEVELOPER_URL),
            InlineKeyboardButton("🆘 Support", url=SUPPORT_CHAT_URL)
        ]
    ])


async def build_start_panel(is_admin: bool) -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton("📚 Commands", callback_data="cb_help_start")]]
    if is_admin:
        buttons.append([InlineKeyboardButton("⚙️ Settings", callback_data="cb_open_panel")])
    return InlineKeyboardMarkup(buttons)


async def build_group_panel(chat_id: int, client: Client) -> tuple[str, InlineKeyboardMarkup]:
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
        [InlineKeyboardButton("◀️ Back", callback_data="panel_back")]
    ]
    return caption, InlineKeyboardMarkup(keyboard)


def register(app: Client) -> None:

    @app.on_message(filters.command("start"))
    async def cmd_start(client: Client, message: Message):
        bot_user = await client.get_me()
        user = message.from_user
        markup = await build_start_panel(await is_admin(client, message))

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
            parse_mode=ParseMode.HTML
        )

    @app.on_message(filters.command("menu") & filters.group)
    async def cmd_menu(client: Client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("🔒 <b>Admins only.</b>", parse_mode=ParseMode.HTML)

        caption, keyboard = await build_group_panel(message.chat.id, client)
        await message.reply_text(caption, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    @app.on_message(filters.command("help"))
    async def cmd_help(client: Client, message: Message):
        await message.reply_text(
            "📌 <b>Available Modules</b>\n\n"
            "➤ BioMode\n➤ AutoDelete\n➤ LinkFilter\n➤ EditMode\n\n"
            "Use <code>/menu</code> in group or <code>/start</code> here to open full panel.",
            reply_markup=get_panel_keyboard(),
            parse_mode=ParseMode.HTML
        )

    @app.on_callback_query()
    async def cb_handler(client: Client, cb: CallbackQuery):
        chat_id = cb.message.chat.id

        if cb.data.startswith("panel_"):
            panels = {
                "panel_biomode": "🛡 <b>BioMode</b>\n\nBlocks messages if user's bio contains links.\nUsage:\n<code>/biolink on</code> | <code>/biolink off</code>",
                "panel_autodelete": "🧹 <b>AutoDelete</b>\n\nAuto-deletes messages after a time.\nUsage:\n<code>/autodelete 60</code>",
                "panel_linkfilter": "🔗 <b>LinkFilter</b>\n\nBlocks messages with links from non-admins.\nUsage:\n<code>/linkfilter on</code> | <code>/linkfilter off</code>",
                "panel_editmode": "✏️ <b>EditMode</b>\n\nDeletes edited messages.\nUsage:\n<code>/editmode on</code> | <code>/editmode off</code>"
            }

            await cb.message.edit_caption(
                caption=panels[cb.data],
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="panel_back")]]),
                parse_mode=ParseMode.HTML
            )
            return await cb.answer()

        elif cb.data == "panel_back":
            await cb.message.edit_caption(
                caption="📚 <b>Bot Command Help</b>\n\nDetails for all features. Tap buttons to learn more.",
                reply_markup=get_panel_keyboard(),
                parse_mode=ParseMode.HTML
            )
            return await cb.answer()

        elif cb.data.startswith("cb_toggle_"):
            if not await is_admin(client, cb.message):
                return await cb.answer("Admins only", show_alert=True)

            setting_map = {
                "cb_toggle_biolink": "biolink",
                "cb_toggle_autodel": "autodelete",
                "cb_toggle_linkfilter": "linkfilter",
                "cb_toggle_editmode": "editmode"
            }

            key = setting_map.get(cb.data)
            if key:
                new_state = await toggle_setting(chat_id, key)
                await cb.answer(f"{key.capitalize()} {'enabled ✅' if new_state == '1' else 'disabled ❌'}")

            caption, markup = await build_group_panel(chat_id, client)
            await cb.message.edit_text(caption, reply_markup=markup, parse_mode=ParseMode.HTML)

    # Admin-only commands
    @app.on_message(filters.command("biolink") & filters.group)
    @catch_errors
    async def cmd_biolink(client: Client, message: Message):
        if not await is_admin(client, message): return
        state = message.text.split(maxsplit=1)[1].lower() if len(message.command) > 1 else None
        if state not in {"on", "off"}:
            return await message.reply("Usage: /biolink on or off", parse_mode=ParseMode.HTML)
        await set_setting(message.chat.id, "biolink", "1" if state == "on" else "0")
        await message.reply(f"BioMode {'enabled ✅' if state == 'on' else 'disabled ❌'}", parse_mode=ParseMode.HTML)

    @app.on_message(filters.command("editmode") & filters.group)
    @catch_errors
    async def cmd_editmode(client: Client, message: Message):
        if not await is_admin(client, message): return
        state = message.text.split(maxsplit=1)[1].lower() if len(message.command) > 1 else None
        if state not in {"on", "off"}:
            return await message.reply("Usage: /editmode on or off", parse_mode=ParseMode.HTML)
        await set_setting(message.chat.id, "editmode", "1" if state == "on" else "0")
        await message.reply(f"EditMode {'enabled ✅' if state == 'on' else 'disabled ❌'}", parse_mode=ParseMode.HTML)

    @app.on_message(filters.command("linkfilter") & filters.group)
    @catch_errors
    async def cmd_linkfilter(client: Client, message: Message):
        if not await is_admin(client, message): return
        state = message.text.split(maxsplit=1)[1].lower() if len(message.command) > 1 else None
        if state not in {"on", "off"}:
            return await message.reply("Usage: /linkfilter on or off", parse_mode=ParseMode.HTML)
        await set_setting(message.chat.id, "linkfilter", "1" if state == "on" else "0")
        await message.reply(f"LinkFilter {'enabled ✅' if state == 'on' else 'disabled ❌'}", parse_mode=ParseMode.HTML)

    @app.on_message(filters.command(["autodelete", "setautodelete"]) & filters.group)
    @catch_errors
    async def cmd_autodelete(client: Client, message: Message):
        if not await is_admin(client, message): return
        if len(message.command) == 1:
            interval = await get_setting(message.chat.id, "autodelete_interval", "60")
            status = await get_setting(message.chat.id, "autodelete", "0")
            return await message.reply(f"AutoDelete: {interval}s ({'ON ✅' if status == '1' else 'OFF ❌'})", parse_mode=ParseMode.HTML)
        try:
            seconds = int(message.command[1])
            if seconds <= 0:
                raise ValueError
        except ValueError:
            return await message.reply("Usage: /autodelete <seconds>", parse_mode=ParseMode.HTML)
        await set_setting(message.chat.id, "autodelete", "1")
        await set_setting(message.chat.id, "autodelete_interval", str(seconds))
        await message.reply(f"AutoDelete set to {seconds}s ✅", parse_mode=ParseMode.HTML)

    @app.on_message(filters.command("autodeleteon") & filters.group)
    async def enable_autodel(client: Client, message: Message):
        await set_setting(message.chat.id, "autodelete", "1")
        await set_setting(message.chat.id, "autodelete_interval", str(DEFAULT_AUTODELETE_SECONDS))
        await message.reply(f"✅ AutoDelete enabled: {DEFAULT_AUTODELETE_SECONDS}s", parse_mode=ParseMode.HTML)

    @app.on_message(filters.command("autodeleteoff") & filters.group)
    async def disable_autodel(client: Client, message: Message):
        await set_setting(message.chat.id, "autodelete", "0")
        await set_setting(message.chat.id, "autodelete_interval", "0")
        await message.reply("🧹 AutoDelete disabled.", parse_mode=ParseMode.HTML)
