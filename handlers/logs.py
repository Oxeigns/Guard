"""Logging handlers for key events."""

from datetime import datetime
from pyrogram import Client
from pyrogram.types import Message

from config import config


async def log(client: Client, text: str) -> None:
    """Send a log message if a log channel is configured."""
    if not config.log_channel_id:
        return
    await client.send_message(config.log_channel_id, text, parse_mode="Markdown")


async def start_log(client: Client, message: Message) -> None:
    """Log when a user starts the bot."""
    user = message.from_user
    stamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    text = (
        f"🧹 **Start**\n"
        f"User: `{user.id}` [{user.mention}]\n"
        f"Time: `{stamp}`"
    )
    await log(client, text)


async def added_to_group(client: Client, message: Message) -> None:
    """Log when the bot is added to a group."""
    inviter = message.from_user.mention if message.from_user else "Unknown"
    text = (
        f"🧹 **Added to Group**\n"
        f"Chat: `{message.chat.id}` {message.chat.title}\n"
        f"By: {inviter}"
    )
    await log(client, text)


async def removed_from_group(client: Client, chat) -> None:
    """Log when the bot is removed from a group."""
    text = (
        f"🧹 **Removed from Group**\n"
        f"Chat: `{chat.id}` {chat.title}"
    )
    await log(client, text)
