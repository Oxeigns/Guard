import asyncio
import logging
from pyrogram import Client, filters, idle

from config import config
import handlers.biofilter  # noqa: F401
import handlers.autodelete  # noqa: F401
import handlers.approval  # noqa: F401
import handlers.panel  # noqa: F401
import handlers.logs


async def main() -> None:
    """Start the Telegram bot."""
    logging.basicConfig(level=getattr(logging, config.log_level.upper(), "INFO"))
    app = Client(
        "guard_bot",
        api_id=config.api_id,
        api_hash=config.api_hash,
        bot_token=config.bot_token,
    )

    @app.on_message(filters.private & filters.command("start"))
    async def start_handler(_, msg):
        await msg.reply_photo(
            config.start_image,
            caption="Welcome!",
            parse_mode="Markdown",
        )
        await handlers.logs.start_log(app, msg)

    @app.on_message(filters.new_chat_members)
    async def join_handler(_, msg):
        if msg.new_chat_members and any(u.is_self for u in msg.new_chat_members):
            await handlers.logs.added_to_group(app, msg)

    @app.on_message(filters.left_chat_member)
    async def left_handler(_, msg):
        if msg.left_chat_member and msg.left_chat_member.is_self:
            await handlers.logs.removed_from_group(app, msg.chat)

    await app.start()
    await idle()
    await app.stop()


if __name__ == "__main__":
    asyncio.run(main())

