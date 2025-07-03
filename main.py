import logging

from pyrogram import Client, filters, idle
from pyrogram.enums import ParseMode

from config import API_HASH, API_ID, BOT_TOKEN, MONGO_URI
from handlers import (
    biofilter,
    approval,
    commands,
    menu,
    panel,
    message_logger,
    autodelete,
)
from utils.storage import close_db, init_db
from utils.errors import catch_errors

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

logger.info(
    "Loaded config: API_ID=%s BOT_TOKEN=%s",
    API_ID,
    BOT_TOKEN[:6] + "***" if BOT_TOKEN else None,
)

bot = Client(
    "moderation-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    parse_mode=ParseMode.HTML,
)


@bot.on_message(filters.command("ping"))
@catch_errors
async def ping_cmd(_, message):
    logger.info("/ping command received")
    await message.reply_text("pong")


@bot.on_message(
    filters.private
    & ~filters.command(["start", "help", "ping", "menu"])
    & ~filters.me,
    group=1,
)
@catch_errors
async def fallback_cmd(_, message):
    """Reply in private chats when no command matches."""
    logger.info("Fallback handler triggered with text: %s", message.text)
    await message.reply_text("Received: " + (message.text or ""))


async def main() -> None:
    logger.info("Initializing database connection")
    await init_db(MONGO_URI)
    for handler in [
        biofilter,
        approval,
        commands,
        menu,
        panel,
        message_logger,
        autodelete,
    ]:
        handler.register(bot)
    async with bot:
        logger.info("Bot started and waiting for events")
        await idle()
    await close_db()
    logger.info("Bot stopped")


if __name__ == "__main__":
    bot.run(main())
