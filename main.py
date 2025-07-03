import os
import asyncio
import logging
import threading

from dotenv import load_dotenv
from flask import Flask
from pyrogram import Client, filters, idle

load_dotenv()

from config import API_HASH, API_ID, BOT_TOKEN, MONGO_URI
from handlers import register_all
from utils.storage import close_db, init_db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Log environment setup for debugging
logger.info(
    "Loaded config: API_ID=%s BOT_TOKEN=%s",
    API_ID,
    BOT_TOKEN[:6] + "***" if BOT_TOKEN else None,
)
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
    logger.info("Starting Flask server on port %s", port)
    flask_app.run(host="0.0.0.0", port=port, use_reloader=False)

def register_handlers() -> None:
    logger.info("Registering handlers")
    register_all(bot)

    @bot.on_message(filters.command("ping"))
    async def ping_cmd(_, message):
        logger.info("/ping command received")
        await message.reply_text("pong")

    @bot.on_message(filters.private & ~filters.command(["start", "help", "menu", "ping"]))
    async def echo_private(_, message):
        logger.info("Private message received: %s", message.text)
        await message.reply_text(f"Echo: {message.text}")

async def main() -> None:
    logger.info("Initializing database connection")
    await init_db(MONGO_URI)
    register_handlers()
    await bot.start()
    logger.info("Bot started and waiting for events")
    await idle()
    await bot.stop()
    await close_db()
    logger.info("Bot stopped")

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    logger.info("Flask thread started")
    try:
        asyncio.run(main())
    except Exception:
        logger.exception("Bot crashed")
