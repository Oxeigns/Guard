import asyncio
import logging
import os

from pyrogram import Client, idle
from pyrogram.enums import ParseMode

from config import (
    API_HASH,
    API_ID,
    BOT_TOKEN,
    MONGO_URI,
    MONGO_DB,
    LOG_LEVEL,
)
from handlers import register_all
from utils.db import init_db, close_db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL, logging.INFO),
)
logger = logging.getLogger(__name__)

BOT_USERNAME = os.getenv("BOT_USERNAME", "OxeignBot")
PANEL_IMAGE_URL = os.getenv("PANEL_IMAGE_URL")
SUPPORT_CHAT_URL = os.getenv("SUPPORT_CHAT_URL", "https://t.me/botsyard")
DEVELOPER_URL = os.getenv("DEVELOPER_URL", "https://t.me/oxeign")

app = Client(
    "oxygen-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    parse_mode=ParseMode.HTML,
)


async def main() -> None:
    logger.info("Initializing database connection")
    await init_db(MONGO_URI, MONGO_DB)
    register_all(app)
    async with app:
        logger.info("Bot started and waiting for events")
        await idle()
    await close_db()
    logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
