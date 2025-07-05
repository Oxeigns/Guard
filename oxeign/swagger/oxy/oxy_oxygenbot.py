import logging
import asyncio
from pyrogram import Client, idle
from pyrogram.enums import ParseMode
from config import API_ID, API_HASH, BOT_TOKEN, MONGO_URI, MONGO_DB, LOG_LEVEL
from handlers import register_all
from utils.db import init_db, close_db
from utils.errors import catch_errors

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL, logging.INFO),
)
logger = logging.getLogger(__name__)

bot = Client(
    "oxygen-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    parse_mode=ParseMode.HTML,
)


@bot.on_message(filters.command("ping"))
@catch_errors
async def _ping(_, message):
    await message.reply_text("🏓 Pong!")


async def main():
    logger.info("🚀 Starting bot")
    await init_db(MONGO_URI, MONGO_DB)
    register_all(bot)

    async with bot:
        logger.info("🤖 Bot started and listening...")
        await idle()

    await close_db()
    logger.info("🛑 Bot stopped")
