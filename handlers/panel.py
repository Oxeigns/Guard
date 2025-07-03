"""Control panel with inline buttons."""

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from utils.storage import toggle_bio_filter, get_bio_filter, set_autodelete, get_autodelete
from utils.perms import is_admin

PANEL_BUTTONS = [
    [InlineKeyboardButton("🛡 Bio Filter Settings", callback_data="toggle_bio")],
    [InlineKeyboardButton("🕒 AutoDelete Settings", callback_data="autodelete")],
    [
        InlineKeyboardButton("✅ Approve", callback_data="approve"),
        InlineKeyboardButton("❌ Unapprove", callback_data="unapprove"),
    ],
    [InlineKeyboardButton("📋 View Approved", callback_data="viewapproved")],
    [InlineKeyboardButton("📣 Support", url="https://t.me/botsyard"),
     InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/oxeigm")],
    [InlineKeyboardButton("❎ Close Panel", callback_data="close")],
]


def register(app: Client):
    @app.on_message(filters.command("panel") & filters.group)
    async def open_panel(client: Client, message: Message):
        if not await is_admin(client, message):
            return
        await message.reply_text(
            "**Control Panel**",
            reply_markup=InlineKeyboardMarkup(PANEL_BUTTONS),
            parse_mode="Markdown",
        )

    @app.on_callback_query(filters.regex("^toggle_bio"))
    async def toggle_bio_cb(client: Client, query: CallbackQuery):
        if not await is_admin(client, query.message):
            await query.answer("Admins only.", show_alert=True)
            return
        state = await toggle_bio_filter(query.message.chat.id)
        await query.answer(
            "Bio filter enabled" if state else "Bio filter disabled",
            show_alert=True,
        )

    @app.on_callback_query(filters.regex("^autodelete"))
    async def autodelete_menu(client: Client, query: CallbackQuery):
        if not await is_admin(client, query.message):
            await query.answer("Admins only.", show_alert=True)
            return
        buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("12h", callback_data="ad_43200"),
                 InlineKeyboardButton("24h", callback_data="ad_86400")],
                [InlineKeyboardButton("Off", callback_data="ad_0")],
            ]
        )
        await query.message.edit_text("**AutoDelete Settings**", reply_markup=buttons)

    @app.on_callback_query(filters.regex("^ad_"))
    async def set_auto_cb(client: Client, query: CallbackQuery):
        if not await is_admin(client, query.message):
            await query.answer("Admins only.", show_alert=True)
            return
        seconds = int(query.data.split("_", 1)[1])
        await set_autodelete(query.message.chat.id, seconds)
        await query.answer("Updated", show_alert=True)
        await query.message.delete()

    @app.on_callback_query(filters.regex("^viewapproved"))
    async def view_approved_cb(client: Client, query: CallbackQuery):
        from utils.storage import get_approved

        users = await get_approved(query.message.chat.id)
        text = "**Approved Users:**\n" + ("\n".join(f"`{u}`" for u in users) if users else "None")
        await query.message.edit_text(text, parse_mode="Markdown")

    @app.on_callback_query(filters.regex("^close"))
    async def close_panel_cb(client: Client, query: CallbackQuery):
        await query.message.delete()

    @app.on_callback_query(filters.regex("^approve$"))
    async def approve_info(client: Client, query: CallbackQuery):
        await query.answer()
        await query.message.edit_text(
            "Reply to a user's message with /approve",
            parse_mode="Markdown",
        )

    @app.on_callback_query(filters.regex("^unapprove$"))
    async def unapprove_info(client: Client, query: CallbackQuery):
        await query.answer()
        await query.message.edit_text(
            "Reply to a user's message with /unapprove",
            parse_mode="Markdown",
        )
