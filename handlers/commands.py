"""Basic bot commands."""

import logging
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from config import UPDATE_CHANNEL_ID, SUPPORT_CHAT_URL, DEVELOPER_URL
from utils.perms import is_member_of

logger = logging.getLogger(__name__)


def register(app: Client):
    @app.on_message(filters.command("start"))
    async def start_cmd(client: Client, message: Message):
        logger.info("/start from %s", message.chat.id)
        if message.chat.type != "private":
            await message.reply_text("ℹ️ Please DM me for details.")
            return

        if UPDATE_CHANNEL_ID:
            if not await is_member_of(client, UPDATE_CHANNEL_ID, message.from_user.id):
                button = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Join Updates",
                                url=f"https://t.me/{UPDATE_CHANNEL_ID}",
                            )
                        ]
                    ]
                )
                await message.reply_text(
                    "Please join the update channel to use me.",
                    reply_markup=button,
                )
                return

        user = message.from_user
        profile = [
            "**👤 Profile**",
            f"**Name:** {user.mention}",
            f"**ID:** `{user.id}`",
        ]
        if user.username:
            profile.append(f"**Username:** @{user.username}")
        text = "\n".join(profile)

        me = await client.get_me()
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "➕ Add to Group",
                        url=f"https://t.me/{me.username}?startgroup=true",
                    )
                ],
                [InlineKeyboardButton("ℹ️ Help", callback_data="help_tab")],
                [
                    InlineKeyboardButton("👤 Developer", url=DEVELOPER_URL),
                    InlineKeyboardButton("📣 Support", url=SUPPORT_CHAT_URL),
                ],
            ]
        )
        await message.reply_text(text, reply_markup=buttons, parse_mode="Markdown")

    @app.on_message(filters.command("help"))
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
            "/panel - open control panel"
        )
        await message.reply_text(help_text, parse_mode="Markdown")

    @app.on_message(filters.command("auth"))
    async def auth_cmd(client: Client, message: Message):
        logger.info("/auth from %s", message.chat.id)
        if message.chat.type == "private":
            await message.reply_text("This command can only be used in groups.")
            return
        try:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            await message.reply_text(f"Your status: `{member.status}`", parse_mode="Markdown")
        except Exception as exc:
            logger.warning("auth check failed: %s", exc)
            await message.reply_text("Couldn't check your status.")

    @app.on_callback_query(filters.regex("^help_tab$"))
    async def help_cb(client: Client, query: CallbackQuery):
        logger.info("help callback from %s", query.from_user.id)
        help_text = (
            "**Commands:**\n"
            "/approve - approve user\n"
            "/unapprove - unapprove user\n"
            "/viewapproved - list approved\n"
            "/setautodelete <sec> - auto delete messages\n"
            "/panel - open control panel"
        )
        await query.message.edit_text(help_text, parse_mode="Markdown")

