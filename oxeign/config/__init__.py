import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
OWNER_ID = int(os.getenv("OWNER_ID"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", 0))

# Derived constants
BOT_NAME = os.getenv('BOT_NAME', 'MasterGuardianBot')
SUPPORT_LINK = os.getenv('SUPPORT_LINK', 'https://t.me/Botsyard')
DEV_LINK = os.getenv('DEV_LINK', 'https://t.me/oxeign')
PANEL_HEADER_URL = os.getenv('PANEL_HEADER_URL', 'https://files.catbox.moe/uvqeln.jpg')
