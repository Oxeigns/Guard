"""Basic bot commands."""

import logging
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, ChatPermissions

from utils.perms import is_admin


from utils.errors import catch_errors

logger = logging.getLogger(__name__)


def register(app: Client) -> None:

    @app.on_message(filters.command("help"))
    @catch_errors
    async def help_cmd(client: Client, message: Message):
        logger.info("/help from %s", message.chat.id)
        if message.chat.type != "private":
            await message.reply_text("ℹ️ Please DM me for help.")
            return

        help_text = (
            "<b>Commands:</b>\n"
            "/approve - approve user\n"
            "/unapprove - unapprove user\n"
            "/viewapproved - list approved\n"
            "/setautodelete <sec> - auto delete messages\n"
            "/mute - mute replied user\n"
            "/kick - kick replied user\n"
            "/ban - ban replied user\n"
            "/start - open control panel"
        )
        await message.reply_text(help_text)

    @app.on_message(filters.command("auth"))
    @catch_errors
    async def auth_cmd(client: Client, message: Message):
        logger.info("/auth from %s", message.chat.id)
        if message.chat.type == "private":
            await message.reply_text("This command can only be used in groups.")
            return
        try:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            await message.reply_text(f"Your status: <code>{member.status}</code>")
        except Exception as exc:
            logger.warning("auth check failed: %s", exc)
            await message.reply_text("Couldn't check your status.")

    @app.on_callback_query(filters.regex("^help_tab$"))
    @catch_errors
    async def help_cb(client: Client, query: CallbackQuery):
        logger.info("help callback from %s", query.from_user.id)
        help_text = (
            "<b>Commands:</b>\n"
            "/approve - approve user\n"
            "/unapprove - unapprove user\n"
            "/viewapproved - list approved\n"
            "/setautodelete <sec> - auto delete messages\n"
            "/mute - mute replied user\n"
            "/kick - kick replied user\n"
            "/ban - ban replied user\n"
            "/start - open control panel"
        )
        await query.message.edit_text(help_text)

    @app.on_message(filters.command("mute") & filters.group)
    @catch_errors
    async def mute_cmd(client: Client, message: Message):
        logger.info("/mute in %s", message.chat.id)
        if not await is_admin(client, message):
            await message.reply_text("❌ You must be an admin to mute.")
            return
        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.reply_text("Reply to a user to mute.")
            return
        target = message.reply_to_message.from_user
        try:
            await client.restrict_chat_member(message.chat.id, target.id, ChatPermissions())
            await message.reply_text(f"Muted <code>{target.id}</code>")
        except Exception as exc:
            logger.warning("mute failed: %s", exc)
            await message.reply_text("❌ Failed to mute. Do I have permission?")

    @app.on_message(filters.command("kick") & filters.group)
    @catch_errors
    async def kick_cmd(client: Client, message: Message):
        logger.info("/kick in %s", message.chat.id)
        if not await is_admin(client, message):
            await message.reply_text("❌ You must be an admin to kick.")
            return
        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.reply_text("Reply to a user to kick.")
            return
        target = message.reply_to_message.from_user
        try:
            await client.ban_chat_member(message.chat.id, target.id)
            await client.unban_chat_member(message.chat.id, target.id)
            await message.reply_text(f"Kicked <code>{target.id}</code>")
        except Exception as exc:
            logger.warning("kick failed: %s", exc)
            await message.reply_text("❌ Failed to kick. Do I have permission?")

    @app.on_message(filters.command("ban") & filters.group)
    @catch_errors
    async def ban_cmd(client: Client, message: Message):
        logger.info("/ban in %s", message.chat.id)
        if not await is_admin(client, message):
            await message.reply_text("❌ You must be an admin to ban.")
            return
        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.reply_text("Reply to a user to ban.")
            return
        target = message.reply_to_message.from_user
        try:
            await client.ban_chat_member(message.chat.id, target.id)
            await message.reply_text(f"Banned <code>{target.id}</code>")
        except Exception as exc:
            logger.warning("ban failed: %s", exc)
            await message.reply_text("❌ Failed to ban. Do I have permission?")

