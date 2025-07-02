from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from oxeign.config import START_IMAGE, BOT_NAME
from oxeign.utils.cleaner import auto_delete

async def start(client: Client, message):
    text = f"✨ Welcome to <b>{BOT_NAME}</b>!" \
        "\nYour personal guardian at your service."
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📖 Help", callback_data="help")],
            [InlineKeyboardButton("💬 Support", url="https://t.me/botsyard")],
        ]
    )
    reply = (
        await message.reply_photo(START_IMAGE, caption=text, reply_markup=buttons, parse_mode="html")
        if START_IMAGE
        else await message.reply(text, reply_markup=buttons, parse_mode="html")
    )
    client.loop.create_task(auto_delete(client, message, reply))

async def help_cmd(client: Client, message):
    help_text = (
        "<b>Master Guardian Commands</b>\n"
        "• /approve - Allow a user\n"
        "• /disapprove - Revoke approval\n"
        "• /setlongmode &lt;mode&gt;\n"
        "• /setlonglimit &lt;num&gt;\n"
        "• /biolink on|off\n"
        "• /broadcast &lt;text&gt;\n"
        "• /mute /unmute\n"
        "• /ban /unban /kick\n"
        "• /warn - Issue warn\n"
        "• /addsudo /rmsudo\n"
        "• /gban /gunban /gmute /gunmute (sudo)"
    )
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("➕ Add to Chat", url=f"https://t.me/{BOT_NAME}?startgroup=true")],
            [InlineKeyboardButton("💬 Support", url="https://t.me/botsyard")],
        ]
    )
    reply = await message.reply(help_text, reply_markup=buttons, parse_mode="html")
    client.loop.create_task(auto_delete(client, message, reply))

async def help_callback(client: Client, callback_query):
    await callback_query.answer()
    await callback_query.message.delete()
    m = await callback_query.message.reply("/help")
    await help_cmd(client, m)


def register(app: Client):
    app.add_handler(MessageHandler(start, filters.command("start")))
    app.add_handler(MessageHandler(help_cmd, filters.command("help")))
    app.add_handler(CallbackQueryHandler(help_callback, filters.regex("^help$")))
