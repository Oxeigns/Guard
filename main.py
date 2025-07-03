import asyncio
import logging

from pyrogram import Client

from config import BOT_TOKEN, API_ID, API_HASH, MONGO_URI
from handlers import biofilter, autodelete, approval, panel, logs
from utils.storage import init_db, close_db

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


def register_handlers():
    biofilter.register(app)
    autodelete.register(app)
    approval.register(app)
    panel.register(app)
    logs.register(app)


async def main():
    await init_db(MONGO_URI)
    register_handlers()
    async with app:
        logger.info("Bot started")
        await asyncio.Event().wait()
    await close_db()
    logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
