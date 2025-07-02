import logging
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, LOG_LEVEL
from handlers import register_handlers

logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)


def main():
    app = Client("master_guardian", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

    register_handlers(app)

    logger.info("Starting bot...")
    app.run()


if __name__ == "__main__":
    main()
