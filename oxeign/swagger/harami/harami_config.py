import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "oxygen")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
BOT_USERNAME = os.getenv("BOT_USERNAME", "OxygenBot")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID", "-1002822775608"))

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
    missing_str = ", ".join(_missing)
    logger.error("Missing required env vars: %s", missing_str)
    raise RuntimeError(
        "Missing required environment variables: "
        f"{missing_str}. Create a .env file from .env.example and set them."
    )

if not MONGO_URI.startswith(("mongodb://", "mongodb+srv://")):
    logger.error("Invalid MONGO_URI: %s", MONGO_URI)
    raise RuntimeError(
        "Invalid MONGO_URI. It must begin with 'mongodb://' or 'mongodb+srv://'"
    )

# Optional configuration
UPDATE_CHANNEL_ID = int(os.getenv("UPDATE_CHANNEL_ID", "0"))
SUPPORT_CHAT_URL = os.getenv("SUPPORT_CHAT_URL", "https://t.me/botsyard")
DEVELOPER_URL = os.getenv("DEVELOPER_URL", "https://t.me/oxeign")
# Image shown at the top of the settings panel
PANEL_IMAGE_URL = os.getenv("PANEL_IMAGE_URL", "https://files.catbox.moe/uvqeln.jpg")
