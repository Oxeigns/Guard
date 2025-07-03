import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
MONGO_URI = os.getenv("MONGO_URI", "")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "guard")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0"))

_missing = [
    name
    for name, value in {
        "BOT_TOKEN": BOT_TOKEN,
        "API_ID": API_ID,
        "API_HASH": API_HASH,
    }.items()
    if not value
]
if _missing:
    logger.error("Missing required env vars: %s", ", ".join(_missing))
    raise RuntimeError("Required environment variables are missing")

# Optional configuration
UPDATE_CHANNEL_ID = int(os.getenv("UPDATE_CHANNEL_ID", "0"))
SUPPORT_CHAT_URL = os.getenv("SUPPORT_CHAT_URL", "https://t.me/botsyard")
DEVELOPER_URL = os.getenv("DEVELOPER_URL", "https://t.me/oxeign")
# Image shown at the top of the settings panel
BANNER_URL = os.getenv("BANNER_URL", "")
