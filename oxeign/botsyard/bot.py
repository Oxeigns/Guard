from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.enums import ParseMode
from oxeign.config import START_IMAGE, BOT_NAME
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
        f"<b>👋 Welcome to {BOT_NAME}</b>\n\n"
        f"<b>Name:</b> {user.mention()}\n"
        f"<b>ID:</b> <code>{user.id}</code>\n"
        f"<b>Username:</b> {username}\n"
        f"<b>Role:</b> {role.title()}\n"
        f"<b>Groups served:</b> {group_count}"
    )

    rows = [
        [InlineKeyboardButton("🛠 Commands", callback_data="menu"), InlineKeyboardButton("❓ Help", callback_data="help")],
        [InlineKeyboardButton("📣 Support", url="https://t.me/Botsyard"), InlineKeyboardButton("👑 Developer", url="https://t.me/Oxeign")],
        [InlineKeyboardButton("❌ Close", callback_data="close")],
    ]
    buttons = InlineKeyboardMarkup(rows)

    if START_IMAGE:
        reply = await message.reply_photo(START_IMAGE, caption=text, reply_markup=buttons, parse_mode=ParseMode.HTML)
    else:
        reply = await message.reply(text, reply_markup=buttons, parse_mode=ParseMode.HTML)



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
    text = "<b>📚 Help Panel</b>\nSelect a category below."
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Moderation", callback_data="help_moderation"),
             InlineKeyboardButton("Anti-Spam", callback_data="help_antispam")],
            [InlineKeyboardButton("Filters", callback_data="help_filters"),
             InlineKeyboardButton("Approval", callback_data="help_approval")],
            [InlineKeyboardButton("Misc", callback_data="help_misc"),
             InlineKeyboardButton("❌ Close", callback_data="close")],
        ]
    )
    return text, buttons


async def help_cmd(client: Client, message):
    text, buttons = help_content()
    await message.reply(text, reply_markup=buttons, parse_mode=ParseMode.HTML)

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

    rows = []
    for i in range(0, len(cmds), 2):
        pair = cmds[i:i+2]
        rows.append([InlineKeyboardButton(c, callback_data=f"cmd:{c[1:]}") for c in pair])
    rows.append([InlineKeyboardButton("❌ Close", callback_data="close")])

    markup = InlineKeyboardMarkup(rows)
    await message.reply("<b>Available Commands</b>", reply_markup=markup, parse_mode=ParseMode.HTML)

async def help_callback(client: Client, callback_query):
    await callback_query.answer()
    text, buttons = help_content()
    await callback_query.message.edit_text(text, reply_markup=buttons, parse_mode=ParseMode.HTML)

async def help_section_callback(client: Client, callback_query):
    await callback_query.answer()
    section = callback_query.data.split("_")[1]
    if section == "moderation":
        text = "<b>Moderation Commands</b>\n/ban /unban /kick /mute /unmute /warn"
    elif section == "antispam":
        text = "<b>Anti-Spam</b>\n/biolink on|off \n/setlongmode <mode> \n/setlonglimit <num>"
    elif section == "filters":
        text = "<b>Filters</b>\n/blacklist add|remove|list"
    elif section == "approval":
        text = "<b>Approval Mode</b>\n/approve /disapprove"
    else:
        text = "<b>Misc</b>\n/setwelcome <text>\n/broadcast <text>"
    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Back", callback_data="help"), InlineKeyboardButton("❌ Close", callback_data="close")]]
    )
    await callback_query.message.edit_text(text, reply_markup=buttons, parse_mode=ParseMode.HTML)

CMD_HELP = {
    "ban": "Ban a user",
    "unban": "Unban a user",
    "mute": "Mute a user",
    "unmute": "Unmute a user",
    "kick": "Kick a user",
    "warn": "Warn a user",
    "approve": "Approve member",
    "disapprove": "Disapprove member",
    "setautodelete": "Set auto delete seconds",
    "setwelcome": "Set welcome message",
    "blacklist": "Manage blacklist words",
    "biolink": "Toggle bio link filter",
    "setlongmode": "Set long message mode",
    "setlonglimit": "Set long message limit",
    "getconfig": "Show chat config",
    "broadcast": "Broadcast a message",
    "addsudo": "Add sudo user",
    "rmsudo": "Remove sudo user",
}

async def cmd_callback(client: Client, callback_query):
    await callback_query.answer()
    cmd = callback_query.data.split(":", 1)[1]
    desc = CMD_HELP.get(cmd, "No description")
    text = f"<b>/{cmd}</b> - {desc}"
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="menu")], [InlineKeyboardButton("❌ Close", callback_data="close")]])
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
    app.add_handler(CallbackQueryHandler(help_section_callback, filters.regex("^help_")))
    app.add_handler(CallbackQueryHandler(cmd_callback, filters.regex("^cmd:")))
    app.add_handler(CallbackQueryHandler(menu_callback, filters.regex("^menu$")))
    app.add_handler(CallbackQueryHandler(close_callback, filters.regex("^close$")))
