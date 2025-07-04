from pyrogram.types import Message

async def safe_edit_message(message: Message, *, text: str | None = None, caption: str | None = None, **kwargs) -> None:
    """Edit a message only if content differs to avoid MESSAGE_NOT_MODIFIED."""
    if text is not None:
        if message.text == text:
            return
        await message.edit_text(text, **kwargs)
    elif caption is not None:
        if message.caption == caption:
            return
        await message.edit_caption(caption, **kwargs)

