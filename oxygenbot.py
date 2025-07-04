import asyncio
import logging
import os

from pyrogram import Client, idle
from pyrogram.enums import ParseMode

from config import (
    API_ID,
    API_HASH,
    BOT_TOKEN,
    MONGO_URI,
    MONGO_DB,
    LOG_LEVEL,
)
from handlers import register_all
from utils.db import init_db, close_db

# Logging configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
)
logger = logging.getLogger("OxygenBot")

# Optional environment settings
BOT_USERNAME = os.getenv("BOT_USERNAME", "OxeignBot")
PANEL_IMAGE_URL = os.getenv("PANEL_IMAGE_URL", "https://files.catbox.moe/uvqeln.jpg")
SUPPORT_CHAT_URL = os.getenv("SUPPORT_CHAT_URL", "https://t.me/botsyard")
DEVELOPER_URL = os.getenv("DEVELOPER_URL", "https://t.me/oxeign")

# Initialize Pyrogram client
app = Client(
    "oxygen-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    parse_mode=ParseMode.HTML,
)


async def main() -> None:
    logger.info("🔌 Connecting to database...")
    await init_db(MONGO_URI, MONGO_DB)

    logger.info("📦 Registering all handlers...")
    register_all(app)

    logger.info("🤖 Starting bot...")
    async with app:
        logger.info("✅ Bot is now running. Waiting for events...")
        await idle()

    logger.info("🔒 Shutting down bot...")
    await close_db()
    logger.info("🛑 Bot stopped successfully.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("❗ Bot terminated manually.")
