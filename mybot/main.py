import asyncio
import logging
from pyrogram import Client, idle
from pyrogram.enums import ParseMode

from config import API_ID, API_HASH, BOT_TOKEN, MONGO_URI, MONGO_DB, LOG_LEVEL
from handlers import register_all
from utils.db import init_db, close_db
from utils.webhook import delete_webhook

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
)
logger = logging.getLogger(__name__)

# Initialize the bot client
bot = Client(
    "oxygen_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    parse_mode=ParseMode.HTML,
)


async def main() -> None:
    logger.info("🚀 Starting OxygenBot...")

    # Initialize MongoDB
    await init_db(MONGO_URI, MONGO_DB)
    logger.info("✅ MongoDB connected.")

    # Clear old webhooks
    await delete_webhook(BOT_TOKEN)
    logger.info("🔌 Webhook deleted (if any). Switching to polling mode.")

    # Register handlers from all modules
    register_all(bot)

    # Start the bot and listen
    async with bot:
        logger.info("🤖 OxygenBot is live and listening...")
        await idle()

    # Graceful shutdown
    await close_db()
    logger.info("🛑 Bot stopped cleanly.")


if __name__ == "__main__":
    asyncio.run(main())
