import logging
from pyrogram import Client, idle
from pyrogram.enums import ParseMode

from config import API_ID, API_HASH, BOT_TOKEN, MONGO_URI, MONGO_DB, LOG_LEVEL
from handlers import register_all  # ⬅️ This comes from handlers/__init__.py
from utils.db import init_db, close_db
from utils.webhook import delete_webhook

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL, logging.INFO),
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

# Main lifecycle function
async def main() -> None:
    logger.info("🚀 Starting OxygenBot...")

    await init_db(MONGO_URI, MONGO_DB)
    logger.info("✅ MongoDB connected.")

    await delete_webhook(BOT_TOKEN)
    logger.info("🔌 Webhook deleted (if any). Using polling mode.")

    async with bot:
        register_all(bot)
        logger.info("🤖 Bot started. Waiting for events...")
        await idle()

    await close_db()
    logger.info("🛑 Bot shutdown completed. MongoDB closed.")

# Entrypoint
if __name__ == "__main__":
    bot.run(main())
