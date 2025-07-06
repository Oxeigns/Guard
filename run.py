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


async def main() -> None:
    logger.info("\uD83D\uDE80 Starting OxygenBot...")
    await init_db(MONGO_URI, MONGO_DB)
    logger.info("\u2705 MongoDB connected.")
    await delete_webhook(BOT_TOKEN)
    logger.info("\uD83D\uDD0C Webhook deleted (if any). Using polling mode.")
    register_all(bot)
    logger.info("\uD83E\uDD16 Bot is live and listening...")
    await idle()
    await close_db()
    logger.info("\uD83D\uDD1A Bot stopped cleanly.")


if __name__ == "__main__":
    bot.run(main())
