import os
import asyncio
import logging
import threading

from dotenv import load_dotenv
from flask import Flask
from pyrogram import Client, idle

load_dotenv()

from config import API_HASH, API_ID, BOT_TOKEN, MONGO_URI
from handlers import register_all
from utils.storage import close_db, init_db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

bot = Client(
    "moderation-bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH,
)

flask_app = Flask(__name__)

@flask_app.route("/")
def index():
    return "Bot is running"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

def register_handlers() -> None:
    register_all(bot)

async def main() -> None:
    logger.info("Initializing database")
    await init_db(MONGO_URI)
    register_handlers()
    await bot.start()
    logger.info("Bot started")
    await idle()
    await bot.stop()
    await close_db()
    logger.info("Bot stopped")

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    try:
        asyncio.run(main())
    except Exception:
        logger.exception("Bot crashed")
