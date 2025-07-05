import asyncio
import logging
from pyrogram import Client, filters, idle
from pyrogram.enums import ParseMode

from config import API_ID, API_HASH, BOT_TOKEN, MONGO_URI, MONGO_DB, LOG_LEVEL
from handlers import register_all
from utils.db import init_db, close_db
from utils.errors import catch_errors

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL, logging.DEBUG),  # ← force debug level
)
logger = logging.getLogger(__name__)

# Initialize bot client
bot = Client(
    name="sirion-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    parse_mode=ParseMode.HTML,
)


# Ping test command
@bot.on_message(filters.command("ping"))
@catch_errors
async def _ping(_, message):
    logger.debug(f"Received /ping from {message.chat.id}")
    await message.reply_text("🏓 Pong!")


async def main():
    logger.info("🚀 Starting Sirion Bot...")

    try:
        await init_db(MONGO_URI, MONGO_DB)
        logger.info("✅ Connected to MongoDB")
    except Exception as e:
        logger.error(f"❌ MongoDB Connection Failed: {e}")
        return

    # Register all modules
    register_all(bot)
    logger.info("📦 All modules registered")

    # Start client
    async with bot:
        logger.info("🤖 Bot started. Listening for messages...")
        await idle()

    await close_db()
    logger.info("🔌 Bot stopped cleanly")


# Run
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"🔥 Fatal error in bot startup: {e}")
