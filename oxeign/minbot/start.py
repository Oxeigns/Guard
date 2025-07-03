from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.enums import ParseMode

from oxeign.utils.logger import log_to_channel
from oxeign.utils.perms import is_admin
from oxeign.config import BOT_NAME
from .panel import build_panel


async def start_cmd(client: Client, message):
    if message.chat.type in ("supergroup", "group"):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return
        markup = await build_panel(message.chat.id)
        await message.reply("**Control Panel**", reply_markup=markup, parse_mode=ParseMode.MARKDOWN)
    else:
        markup = await build_panel(message.chat.id)
        await message.reply(f"**Welcome to {BOT_NAME}!**", reply_markup=markup, parse_mode=ParseMode.MARKDOWN)
        await log_to_channel(
            client,
            f"#START\nUser: {message.from_user.mention} ({message.from_user.id})",
        )


def register(app: Client):
    app.add_handler(MessageHandler(start_cmd, filters.command(["start", "help"])))
