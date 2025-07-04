import logging
import asyncio

from pyrogram import Client, filters, idle
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from config import API_HASH, API_ID, BOT_TOKEN, MONGO_URI, MONGO_DB, LOG_LEVEL
from handlers import register_all
from utils.db import close_db, init_db
from utils.errors import catch_errors

# Setup Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
)
logger = logging.getLogger("ModerationBot")

# Log token partially for verification without exposure
logger.info(
    "Loaded config: API_ID=%s BOT_TOKEN=%s",
    API_ID,
    BOT_TOKEN[:6] + "***" if BOT_TOKEN else "None",
)

# Initialize Pyrogram Client
bot = Client(
    "moderation-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    parse_mode=ParseMode.HTML,
)

# Basic /ping command
@bot.on_message(filters.command("ping") & filters.private)
@catch_errors
async def ping_cmd(_: Client, message: Message):
    logger.info("/ping command received from %s", message.from_user.id)
    await message.reply_text("🏓 Pong!")

# Fallback handler for private messages
@bot.on_message(filters.private & ~filters.me, group=1)
@catch_errors
async def fallback_cmd(_: Client, message: Message):
    if message.text and message.text.startswith("/"):
        return
    logger.info("Fallback handler triggered with text: %s", message.text)
    await message.reply_text("🤖 Received: " + (message.text or "<empty>"))

# Entry point
async def main() -> None:
    logger.info("🔌 Initializing database connection...")
    await init_db(MONGO_URI, MONGO_DB)

    logger.info("📦 Registering handlers...")
    register_all(bot)

    async with bot:
        logger.info("✅ Bot is up and running.")
        await idle()

    logger.info("🔒 Closing DB connection...")
    await close_db()
    logger.info("🛑 Bot shutdown complete.")

# Start the bot
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.warning("❗ Bot stopped manually.")
