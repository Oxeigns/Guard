from pyrogram import Client
from oxeign.config import API_ID, API_HASH, BOT_TOKEN
from oxeign.minbot import register_handlers
from oxeign.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    app = Client("master_guardian", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

    register_handlers(app)

    logger.info("Starting bot...")
    app.run()


if __name__ == "__main__":
    main()
