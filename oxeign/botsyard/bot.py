from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.enums import ParseMode
from oxeign.config import START_IMAGE, BOT_NAME
from oxeign.utils.cleaner import auto_delete
from oxeign.utils.perms import get_role
from oxeign.utils.logger import log_to_channel
from oxeign.swagger.groups import add_group, get_groups
from datetime import datetime

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
        f"<b>{BOT_NAME}</b> welcomes you, {user.mention()}!\n"
        f"Role: <b>{role.title()}</b>\n"
        f"ID: <code>{user.id}</code>\n"
        f"Username: {username}\n"
        f"Groups served: <b>{group_count}</b>"
    )

    rows = [
        [InlineKeyboardButton("❓ Help", callback_data="help"), InlineKeyboardButton("🛠 Commands", callback_data="menu")],
        [InlineKeyboardButton("📣 Support", url="https://t.me/Botsyard"), InlineKeyboardButton("✖️ Close", callback_data="close")],
    ]
    buttons = InlineKeyboardMarkup(rows)

    if START_IMAGE:
        reply = await message.reply_photo(START_IMAGE, caption=text, reply_markup=buttons, parse_mode=ParseMode.HTML)
    else:
        reply = await message.reply(text, reply_markup=buttons, parse_mode=ParseMode.HTML)

    if message.chat.type != "private":
        client.loop.create_task(auto_delete(client, message, reply))

    log_text = (
        f"#START\n"
        f"Name: {full_name}\n"
        f"ID: {user.id}\n"
        f"Username: {username}\n"
        f"Link: {user.mention('link')}\n"
        f"Timestamp: {datetime.utcnow().isoformat()}\n"
    )
    await log_to_channel(client, log_text)

def help_content():
    text = "<b>Need assistance?</b> Use the buttons below to navigate."
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🛠 Commands", callback_data="menu")],
            [InlineKeyboardButton("💬 Support", url="https://t.me/Botsyard"), InlineKeyboardButton("✖️ Close", callback_data="close")],
        ]
    )
    return text, buttons


async def help_cmd(client: Client, message):
    text, buttons = help_content()
    reply = await message.reply(text, reply_markup=buttons, parse_mode=ParseMode.HTML)
    if message.chat.type != "private":
        client.loop.create_task(auto_delete(client, message, reply))

async def menu_cmd(client: Client, message, user=None):
    user = user or message.from_user
    role = await get_role(client, message.chat.id if message.chat.type != "private" else None, user.id)

    user_cmds = ["/help", "/menu"]
    admin_cmds = [
        "/ban", "/unban", "/mute", "/unmute", "/kick", "/warn",
        "/approve", "/disapprove", "/setautodelete", "/setwelcome",
        "/blacklist", "/biolink", "/setlongmode", "/setlonglimit", "/getconfig",
    ]
    sudo_cmds = ["/gban", "/gunban", "/gmute", "/gunmute", "/broadcast"]
    owner_cmds = ["/addsudo", "/rmsudo"]

    cmds = user_cmds
    if role in {"admin", "sudo", "owner"}:
        cmds += admin_cmds
    if role in {"sudo", "owner"}:
        cmds += sudo_cmds
    if role == "owner":
        cmds += owner_cmds

    box = ["╭── Commands ──╮"]
    for c in cmds:
        box.append(f"│ {c}")
    box.append("╰────────────╯")
    text = "<pre>" + "\n".join(box) + "</pre>"

    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("✖️ Close", callback_data="close")]])
    reply = await message.reply(text, reply_markup=buttons, parse_mode=ParseMode.HTML)
    if message.chat.type != "private":
        client.loop.create_task(auto_delete(client, message, reply))

async def help_callback(client: Client, callback_query):
    await callback_query.answer()
    text, buttons = help_content()
    await callback_query.message.edit_text(text, reply_markup=buttons, parse_mode=ParseMode.HTML)

async def menu_callback(client: Client, callback_query):
    await callback_query.answer()
    await menu_cmd(client, callback_query.message, user=callback_query.from_user)

async def close_callback(client: Client, callback_query):
    await callback_query.answer()
    await callback_query.message.delete()


def register(app: Client):
    app.add_handler(MessageHandler(start, filters.command("start")))
    app.add_handler(MessageHandler(help_cmd, filters.command("help")))
    app.add_handler(MessageHandler(menu_cmd, filters.command("menu")))
    app.add_handler(CallbackQueryHandler(help_callback, filters.regex("^help$")))
    app.add_handler(CallbackQueryHandler(menu_callback, filters.regex("^menu$")))
    app.add_handler(CallbackQueryHandler(close_callback, filters.regex("^close$")))
