import logging
from pyrogram import Client, idle
from pyrogram.enums import ParseMode

from config.settings import API_ID, API_HASH, BOT_TOKEN, MONGO_URI
from handlers import init_all
from utils.db import init_db, close_db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

app = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    parse_mode=ParseMode.HTML,
)


async def main() -> None:
    init_db(MONGO_URI)
    init_all(app)
    async with app:
        logger.info("Bot started")
        await idle()
    await close_db()


if __name__ == "__main__":
    app.run(main())
