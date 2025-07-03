"""Configuration loader for the Telegram Guard bot."""

from dataclasses import dataclass, field
from os import getenv
from dotenv import load_dotenv

load_dotenv()


def _get_int(name: str, default: int = 0) -> int:
    """Safely parse an integer environment variable."""
    value = (getenv(name, str(default)) or str(default)).strip()
    try:
        return int(value)
    except ValueError:
        return default

@dataclass
class Config:
    """Dataclass for global configuration."""

    api_id: int = field(default_factory=lambda: _get_int("API_ID"))
    api_hash: str = getenv("API_HASH", "").strip()
    bot_token: str = getenv("BOT_TOKEN", "").strip()
    mongo_uri: str = getenv("MONGO_URI", "").strip()
    owner_id: int = field(default_factory=lambda: _get_int("OWNER_ID"))
    log_level: str = getenv("LOG_LEVEL", "INFO").strip()
    log_channel_id: int = field(default_factory=lambda: _get_int("LOG_CHANNEL_ID"))
    start_image: str = getenv("START_IMAGE", "").strip()

    def validate(self) -> None:
        """Ensure required configuration values are present."""
        missing = []
        if not self.api_id:
            missing.append("API_ID")
        if not self.api_hash:
            missing.append("API_HASH")
        if not self.bot_token:
            missing.append("BOT_TOKEN")
        if not self.mongo_uri:
            missing.append("MONGO_URI")
        if missing:
            names = ", ".join(missing)
            raise RuntimeError(f"Missing required config values: {names}")


config = Config()
config.validate()
