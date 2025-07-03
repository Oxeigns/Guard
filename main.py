import asyncio
import logging

from pyrogram import Client, idle

from config import API_HASH, API_ID, BOT_TOKEN, MONGO_URI
from handlers import register_all
from utils.storage import close_db, init_db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

app = Client(
    "moderation-bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH,
)


def register_handlers() -> None:
    """Register all handler modules on the global ``app`` instance."""
    register_all(app)


async def main() -> None:
    logger.info("Initializing database")
    await init_db(MONGO_URI)
    register_handlers()
    await app.start()
    logger.info("Bot started")
    await idle()
    await app.stop()
    await close_db()
    logger.info("Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception:  # pragma: no cover - log any startup error
        logger.exception("Bot crashed")
