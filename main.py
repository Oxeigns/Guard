import logging
import asyncio
from pyrogram import Client, filters
from motor.motor_asyncio import AsyncIOMotorClient
from config import BOT_TOKEN, MONGO_URI, LOG_CHANNEL_ID

from handlers import biofilter, autodelete, approval, logs
from utils.storage import db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Client(
    name="TelegramModerationBot",
    bot_token=BOT_TOKEN
)

mongo_client = AsyncIOMotorClient(MONGO_URI)
db.client = mongo_client
db.main = mongo_client.get_default_database()

HELP_TEXT = """**🤖 Telegram Moderation Bot Help Menu**

Commands:
/start - Show this help menu
/approve - Whitelist a user from bio filter
/unapprove - Remove a user from the whitelist
/viewapproved - View all approved users
/setautodelete <seconds> - Set auto-delete delay (0 to disable)
/togglebio - Toggle bio link filter on/off

This bot protects your group from users with promotional links in their bio and handles spam via a progressive warning system.

🔐 Admins only can use moderation commands."""

@app.on_message(filters.command("start") & filters.private)
async def start_private(client, message):
    await message.reply_text(HELP_TEXT, parse_mode="Markdown")
    await logs.log_event("Bot started in private chat", message.from_user)

@app.on_message(filters.command("start") & filters.group)
async def start_group(client, message):
    await message.reply_text("✅ Bot is active.")
    await logs.log_event("Bot added to a group", message.chat)

@app.on_my_chat_member()
async def monitor_membership(client, message):
    status = message.new_chat_member.status
    if status == "kicked":
        await logs.log_event("Bot was kicked from a group", message.chat)
    elif status == "member":
        await logs.log_event("Bot was added to a group", message.chat)

async def main():
    biofilter.register(app)
    autodelete.register(app)
    approval.register(app)
    logs.register(app)

    await app.start()
    logger.info("Bot has started.")
    await idle()
    await app.stop()
    logger.info("Bot has stopped.")

if __name__ == "__main__":
    from pyrogram import idle
    asyncio.run(main())
