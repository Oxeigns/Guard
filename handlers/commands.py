"""Basic bot commands."""

import logging
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery


from utils.errors import catch_errors

logger = logging.getLogger(__name__)


def init(app: Client) -> None:

    @app.on_message(filters.command("help"))
    @catch_errors
    async def help_cmd(client: Client, message: Message):
        logger.info("/help from %s", message.chat.id)
        if message.chat.type != "private":
            await message.reply_text("ℹ️ Please DM me for help.")
            return

        help_text = (
            "**Commands:**\n"
            "/approve - approve user\n"
            "/unapprove - unapprove user\n"
            "/viewapproved - list approved\n"
            "/setautodelete <sec> - auto delete messages\n"
            "/start - open control panel"
        )
        await message.reply_text(help_text, parse_mode="markdown")

    @app.on_message(filters.command("auth"))
    @catch_errors
    async def auth_cmd(client: Client, message: Message):
        logger.info("/auth from %s", message.chat.id)
        if message.chat.type == "private":
            await message.reply_text("This command can only be used in groups.")
            return
        try:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            await message.reply_text(f"Your status: `{member.status}`", parse_mode="markdown")
        except Exception as exc:
            logger.warning("auth check failed: %s", exc)
            await message.reply_text("Couldn't check your status.")

    @app.on_callback_query(filters.regex("^help_tab$"))
    @catch_errors
    async def help_cb(client: Client, query: CallbackQuery):
        logger.info("help callback from %s", query.from_user.id)
        help_text = (
            "**Commands:**\n"
            "/approve - approve user\n"
            "/unapprove - unapprove user\n"
            "/viewapproved - list approved\n"
            "/setautodelete <sec> - auto delete messages\n"
            "/start - open control panel"
        )
        await query.message.edit_text(help_text, parse_mode="markdown")

