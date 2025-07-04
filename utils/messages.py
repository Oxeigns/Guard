import logging
from pyrogram.types import Message

logger = logging.getLogger(__name__)

async def safe_edit_message(message: Message, *, text: str | None = None, caption: str | None = None, **kwargs) -> None:
    """Edit a message only if content differs to avoid MESSAGE_NOT_MODIFIED."""
    if text is not None:
        if message.text == text:
            return
        try:
            await message.edit_text(text, **kwargs)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Failed to edit message %s in %s: %s",
                message.id,
                message.chat.id,
                exc,
            )
    elif caption is not None:
        if message.caption == caption:
            return
        try:
            await message.edit_caption(caption, **kwargs)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Failed to edit caption for %s in %s: %s",
                message.id,
                message.chat.id,
                exc,
            )

