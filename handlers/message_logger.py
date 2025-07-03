"""Log every incoming update."""

import logging
from pyrogram import Client, filters
from pyrogram.types import Message

from utils.errors import catch_errors

logger = logging.getLogger(__name__)


def register(app: Client) -> None:
    @app.on_message(filters.all, group=-1)
    @catch_errors
    async def log_messages(client: Client, message: Message):
        user = message.from_user
        logger.info(
            "msg in %s from %s: %s",
            message.chat.id,
            user.id if user else "?",
            (message.text or message.caption or "<non-text>")[:100],
        )

