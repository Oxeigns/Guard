import asyncio
import logging
from pyrogram import Client, filters, idle
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from config import API_ID, API_HASH, BOT_TOKEN, MONGO_URI, MONGO_DB, LOG_LEVEL
from handlers import register_all
from utils.db import init_db, close_db
from utils.errors import catch_errors

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL, logging.DEBUG),  # Force debug logs
)
logger = logging.getLogger(__name__)

# Initialize bot client
bot = Client(
    "sirion-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    parse_mode=ParseMode.HTML,
)


# Health check command
@bot.on_message(filters.command("ping"))
@catch_errors
async def _ping(_, message: Message):
    logger.debug(f"📡 Received /ping from {message.chat.id}")
    await message.reply_text("🏓 Pong!")


# ID command (optional, use if not already in general.py)
@bot.on_message(filters.command("id"))
@catch_errors
async def _id(_, message: Message):
    user = message.from_user
    if message.chat.type in ["group", "supergroup"]:
        text = f"<b>Chat ID:</b> <code>{message.chat.id}</code>\n<b>User ID:</b> <code>{user.id}</code>"
    else:
        text = f"<b>Your ID:</b> <code>{user.id}</code>"
    await message.reply_text(text)


# TEMP: Catch all messages for debug
@bot.on_message(filters.all)
@catch_errors
async def debug_all(_, message: Message):
    logger.debug(f"📥 Received message in chat {message.chat.id}: {message.text}")
    # Optional reply to confirm reception
    if message.text:
        await message.reply_text("📨 I received your message.")


async def main():
    logger.info("🚀 Starting Sirion Bot...")

    try:
        await init_db(MONGO_URI, MONGO_DB)
        logger.info("✅ Connected to MongoDB")
    except Exception as e:
        logger.error(f"❌ MongoDB Connection Failed: {e}")
        return

    # Register command and callback handlers
    register_all(bot)
    logger.info("📦 All modules registered")

    # Start bot
    async with bot:
        logger.info("🤖 Bot started. Listening for messages...")
        await idle()

    await close_db()
    logger.info("🛑 Bot stopped cleanly")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"🔥 Fatal error in bot startup: {e}")
