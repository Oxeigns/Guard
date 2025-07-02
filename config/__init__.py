import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
MONGO_URI = os.getenv('MONGO_URI')
OWNER_ID = int(os.getenv('OWNER_ID'))
SUDO_USERS = list(map(int, os.getenv('SUDO_USERS', str(OWNER_ID)).split(',')))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Derived constants
BOT_NAME = os.getenv('BOT_NAME', 'MasterGuardianBot')
