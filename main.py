import os
import logging
import threading

from flask import Flask
from pyrogram import Client, filters, idle

from config import API_HASH, API_ID, BOT_TOKEN, MONGO_URI
from handlers import init_all
from utils.storage import close_db, init_db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

logger.info(
    "Loaded config: API_ID=%s BOT_TOKEN=%s",
    API_ID,
    BOT_TOKEN[:6] + "***" if BOT_TOKEN else None,
)

bot = Client(
    "moderation-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    parse_mode="markdown",
)

flask_app = Flask(__name__)


@flask_app.route("/")
def index() -> str:
    return "Bot is running"


def run_flask() -> None:
    port = int(os.environ.get("PORT", 10000))
    logger.info("Starting Flask server on port %s", port)
    flask_app.run(host="0.0.0.0", port=port, use_reloader=False)


@bot.on_message(filters.command("ping"))
async def ping_cmd(_, message):
    logger.info("/ping command received")
    await message.reply_text("pong")


@bot.on_message(
    filters.private
    & ~filters.command(["start", "help", "ping", "menu"])
    & ~filters.me,
    group=1,
)
async def fallback_cmd(_, message):
    """Reply in private chats when no command matches."""
    logger.info("Fallback handler triggered with text: %s", message.text)
    await message.reply_text("Received: " + (message.text or ""))


async def main() -> None:
    logger.info("Initializing database connection")
    await init_db(MONGO_URI)
    init_all(bot)
    logger.info("Bot started and waiting for events")
    await idle()
    await close_db()
    logger.info("Bot stopped")


if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("Flask thread started")
    bot.run(main())
