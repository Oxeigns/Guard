import logging
from pyrogram import Client, filters, idle
from pyrogram.enums import ParseMode
from config import API_HASH, API_ID, BOT_TOKEN, MONGO_URI, MONGO_DB, LOG_LEVEL
from handlers import register_all
from utils.db import init_db, close_db
from utils.errors import catch_errors

# --- Logging Setup ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL, logging.INFO),
)
logger = logging.getLogger("main")

logger.info("Loaded config: API_ID=%s | BOT_TOKEN=%s", API_ID, BOT_TOKEN[:6] + "***")

# --- Pyrogram Bot Instance ---
bot = Client(
    name="moderation-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    parse_mode=ParseMode.HTML,
)


# --- Health Check ---
@bot.on_message(filters.command("ping") & filters.private)
@catch_errors
async def ping_cmd(_, message):
    logger.info("/ping command received")
    await message.reply_text("🏓 Pong!")


# --- Fallback Reply in DMs ---
@bot.on_message(filters.private & ~filters.me, group=999)
@catch_errors
async def fallback(_, message):
    if message.text and message.text.startswith("/"):
        return
    logger.info("DM fallback triggered: %s", message.text or "<no text>")
    await message.reply_text("🤖 I'm not sure how to respond to that.")


# --- Startup ---
async def main():
    logger.info("🔌 Initializing MongoDB connection")
    await init_db(MONGO_URI, MONGO_DB)

    logger.info("⚙️ Registering all handlers")
    register_all(bot)

    async with bot:
        logger.info("✅ Bot started. Awaiting events...")
        await idle()

    logger.info("🛑 Stopping... Closing DB connection")
    await close_db()
    logger.info("✅ Bot stopped cleanly.")


if __name__ == "__main__":
    bot.run(main())
