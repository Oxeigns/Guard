from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.enums import ParseMode
from oxeign.config import START_IMAGE, BOT_NAME
from oxeign.utils.cleaner import auto_delete
from oxeign.utils.perms import get_role
from oxeign.utils.logger import log_to_channel
from oxeign.swagger.groups import add_group, get_groups

async def start(client: Client, message):
    user = message.from_user
    role = await get_role(client, None, user.id)
    full_name = " ".join(filter(None, [user.first_name, user.last_name]))
    username = f"@{user.username}" if user.username else "N/A"
    groups = await get_groups()
    group_count = len(groups)
    if message.chat.type in ("supergroup", "group"):
        await add_group(message.chat.id)
    text = (
        f"<b>{full_name}</b>\n"
        f"ID: <code>{user.id}</code>\n"
        f"Username: {username}\n"
        f"Role: <b>{role}</b>\n"
        f"Groups: {group_count}\n\n"
        f"Welcome to <b>{BOT_NAME}</b>, your premium moderation assistant."
    )
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🛠 Commands", callback_data="menu"), InlineKeyboardButton("❓ Help", callback_data="help")],
            [InlineKeyboardButton("📚 How It Works", url="https://t.me/Botsyard"), InlineKeyboardButton("📣 Support", url="https://t.me/Botsyard")],
        ]
    )
    reply = (
        await message.reply_photo(START_IMAGE, caption=text, reply_markup=buttons, parse_mode=ParseMode.HTML)
        if START_IMAGE
        else await message.reply(text, reply_markup=buttons, parse_mode=ParseMode.HTML)
    )
    client.loop.create_task(auto_delete(client, message, reply))
    await log_to_channel(client, f"/start by {user.id}")

async def help_cmd(client: Client, message):
    help_text = (
        "<b>Oxeign Guard Commands</b>\n"
        "• /menu - Command list\n"
        "• /ban /unban /mute /unmute\n"
        "• /addsudo /rmsudo\n"
        "• /blacklist add|remove|list\n"
        "• /setautodelete &lt;sec&gt;\n"
        "• /setwelcome &lt;text&gt;\n"
        "• /broadcast &lt;text&gt;\n"
    )
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("➕ Add to Chat", url=f"https://t.me/{BOT_NAME}?startgroup=true")],
            [InlineKeyboardButton("💬 Support", url="https://t.me/botsyard")],
        ]
    )
    reply = await message.reply(help_text, reply_markup=buttons, parse_mode=ParseMode.HTML)
    client.loop.create_task(auto_delete(client, message, reply))

async def menu_cmd(client: Client, message):
    text = (
        "<b>Command Menu</b>\n"
        "/ban /unban /mute /unmute\n"
        "/addsudo /rmsudo\n"
        "/blacklist add|remove|list\n"
        "/setautodelete <sec>\n"
        "/setwelcome <text>\n"
        "/broadcast <text>"
    )
    reply = await message.reply(text, parse_mode=ParseMode.HTML)
    client.loop.create_task(auto_delete(client, message, reply))

async def help_callback(client: Client, callback_query):
    await callback_query.answer()
    await callback_query.message.delete()
    m = await callback_query.message.reply("/help")
    await help_cmd(client, m)

async def menu_callback(client: Client, callback_query):
    await callback_query.answer()
    await callback_query.message.delete()
    m = await callback_query.message.reply("/menu")
    await menu_cmd(client, m)


def register(app: Client):
    app.add_handler(MessageHandler(start, filters.command("start")))
    app.add_handler(MessageHandler(help_cmd, filters.command("help")))
    app.add_handler(MessageHandler(menu_cmd, filters.command("menu")))
    app.add_handler(CallbackQueryHandler(help_callback, filters.regex("^help$")))
    app.add_handler(CallbackQueryHandler(menu_callback, filters.regex("^menu$")))
