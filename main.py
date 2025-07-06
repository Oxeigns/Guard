import logging
from pyrogram import Client, filters, idle
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from config import (
    API_ID,
    API_HASH,
    BOT_TOKEN,
    MONGO_URI,
    MONGO_DB,
    LOG_LEVEL,
)
from handlers import register_all
from utils.db import init_db, close_db
from utils.webhook import delete_webhook

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL, logging.INFO),
)
logger = logging.getLogger(__name__)

bot = Client(
    "oxygen_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    parse_mode=ParseMode.HTML,
)


@bot.on_message(filters.command("start") & (filters.private | filters.group))
async def start_cmd(client: Client, message: Message) -> None:
    """Reply to /start commands in groups and private chats."""
    logger.info("[START] %s in chat %s", message.from_user.id, message.chat.id)
    await message.reply_text(
        "👋 Hello! I'm alive and ready to moderate your groups."
    )


async def main() -> None:
    """Initialize components, register handlers and run the bot."""
    logger.info("🚀 Starting OxygenBot...")
    await init_db(MONGO_URI, MONGO_DB)
    logger.info("✅ MongoDB connected.")
    await delete_webhook(BOT_TOKEN)
    logger.info("🔌 Webhook deleted (if any). Using polling mode.")
    register_all(bot)
    logger.info("🤖 Bot is live and listening...")
    await idle()
    await close_db()
    logger.info("🔚 Bot stopped cleanly.")


if __name__ == "__main__":
    bot.run(main())
