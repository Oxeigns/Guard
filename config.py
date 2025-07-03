import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "guard")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))

# Optional configuration
UPDATE_CHANNEL_ID = int(os.getenv("UPDATE_CHANNEL_ID", "0"))
SUPPORT_CHAT_URL = os.getenv("SUPPORT_CHAT_URL", "https://t.me/botsyard")
DEVELOPER_URL = os.getenv("DEVELOPER_URL", "https://t.me/oxeign")
# Image shown at the top of the settings panel
BANNER_URL = os.getenv("BANNER_URL", "")
