import logging
from pyrogram import Client, filters, idle
from pyrogram.enums import ParseMode

from config import API_HASH, API_ID, BOT_TOKEN, MONGO_URI, MONGO_DB, LOG_LEVEL
from handlers import register_all
from utils.db import init_db, close_db
from utils.errors import catch_errors
from utils.webhook import delete_webhook

# --- Logging Setup ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
)
logger = logging.getLogger("oxygen.main")

logger.info("🔧 Loaded config | API_ID=%s | BOT_TOKEN=%s", API_ID, BOT_TOKEN[:6] + "****")

# --- Bot Client ---
bot = Client(
    "oxygenbot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    parse_mode=ParseMode.HTML,
)


# --- Ping Command for Health Check ---
@bot.on_message(filters.command("ping") & filters.private)
@catch_errors
async def ping_cmd(_, message):
    logger.info("✅ /ping received from %s", message.from_user.id)
    await message.reply_text("🏓 Pong!")


# --- Optional: Fallback for unrecognized private messages ---
@bot.on_message(filters.private & ~filters.command(["ping", "start", "help"]) & ~filters.me, group=999)
@catch_errors
async def fallback(_, message):
    if message.text:
        logger.debug("Fallback triggered: %s", message.text.strip())
        await message.reply_text("🤖 Sorry, I didn't understand that. Try /start.")


# --- Bot Startup Logic ---
async def main():
    logger.info("🔌 Connecting to MongoDB...")
    await init_db(MONGO_URI, MONGO_DB)

    logger.info("🧹 Deleting old webhook (if any)...")
    await delete_webhook(BOT_TOKEN)

    logger.info("📦 Registering all handlers...")
    register_all(bot)

    async with bot:
        logger.info("🤖 Bot is up and running.")
        await idle()

    logger.info("🛑 Shutting down...")
    await close_db()
    logger.info("✅ Shutdown complete.")


if __name__ == "__main__":
    bot.run(main())
