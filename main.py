import asyncio
import logging

from pyrogram import Client

from config import BOT_TOKEN, MONGO_URI
from handlers import biofilter, autodelete, approval, panel, logs
from utils.storage import init_db, close_db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

app = Client("moderation-bot", bot_token=BOT_TOKEN)


def register_handlers():
    biofilter.register(app)
    autodelete.register(app)
    approval.register(app)
    panel.register(app)
    logs.register(app)


async def main():
    await init_db(MONGO_URI)
    register_handlers()
    await app.start()
    logger.info("Bot started")
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        asyncio.run(close_db())
        app.stop()
        logger.info("Bot stopped")
