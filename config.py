"""Configuration loader for the Telegram Guard bot."""

from dataclasses import dataclass
from os import getenv
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    """Dataclass for global configuration."""

    api_id: int = int(getenv("API_ID", 0))
    api_hash: str = getenv("API_HASH", "")
    bot_token: str = getenv("BOT_TOKEN", "")
    mongo_uri: str = getenv("MONGO_URI", "")
    owner_id: int = int(getenv("OWNER_ID", 0))
    log_level: str = getenv("LOG_LEVEL", "INFO")
    log_channel_id: int = int(getenv("LOG_CHANNEL_ID", 0))
    start_image: str = getenv("START_IMAGE", "")


config = Config()
