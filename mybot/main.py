import asyncio
import logging
from pyrogram import Client, filters, idle
from pyrogram.enums import ParseMode

from .config import API_ID, API_HASH, BOT_TOKEN, MONGO_URI, MONGO_DB, LOG_LEVEL
from .handlers import register_all
from .utils.db import init_db, close_db
from .utils.errors import catch_errors

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL, logging.INFO),
)
logger = logging.getLogger(__name__)

bot = Client(
    "mybot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    parse_mode=ParseMode.HTML,
)

@bot.on_message(filters.command("ping"))
@catch_errors
async def _ping(_, message):
    await message.reply_text("🏓 Pong!")


async def main() -> None:
    logger.info("🚀 Starting bot")
    await init_db(MONGO_URI, MONGO_DB)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Cleared any existing webhook")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to delete webhook: %s", exc)
    register_all(bot)
    async with bot:
        logger.info("🤖 Bot started and listening...")
        await idle()
    await close_db()
    logger.info("🛑 Bot stopped")

if __name__ == "__main__":
    asyncio.run(main())
