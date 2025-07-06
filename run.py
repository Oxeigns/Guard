import asyncio
import logging
from pyrogram import Client, idle
from pyrogram.enums import ParseMode
from config import API_ID, API_HASH, BOT_TOKEN, MONGO_URI, MONGO_DB, LOG_LEVEL
from handlers import register_all
from utils.db import init_db, close_db
from utils.webhook import delete_webhook

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL, logging.INFO),
)
logger = logging.getLogger(__name__)

bot = Client(
    "oxygen_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    parse_mode=ParseMode.HTML,
)

async def main():
    logger.info("🚀 Starting OxygenBot...")
    await init_db(MONGO_URI, MONGO_DB)
    await delete_webhook(BOT_TOKEN)
    await bot.start()  # Start bot explicitly
    register_all(bot)  # Now register handlers
    logger.info("🤖 Bot is live and listening...")
    await idle()
    await bot.stop()
    await close_db()
    logger.info("🔚 Bot stopped cleanly.")

if __name__ == "__main__":
    asyncio.run(main())  # ✅ Use asyncio.run, not bot.run
