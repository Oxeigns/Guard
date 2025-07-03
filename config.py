"""Configuration loader for the Telegram Guard bot."""

from dataclasses import dataclass
from os import getenv
from typing import Any, Callable

from dotenv import load_dotenv

load_dotenv()


def get_env(name: str, default: Any = "", *, cast: Callable[[str], Any] | None = None) -> Any:
    """Return an environment variable with optional casting."""
    value = getenv(name)
    if value is None or value == "":
        return default
    if cast is None or cast is str:
        return value
    if cast is bool:
        return value.lower() in {"1", "true", "yes", "on"}
    try:
        return cast(value)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Invalid value for {name}: {value}") from exc

@dataclass
class Config:
    """Dataclass for global configuration."""

    api_id: int = get_env("API_ID", 0, cast=int)
    api_hash: str = get_env("API_HASH", "")
    bot_token: str = get_env("BOT_TOKEN", "")
    mongo_uri: str = get_env("MONGO_URI", "")
    owner_id: int = get_env("OWNER_ID", 0, cast=int)
    log_level: str = get_env("LOG_LEVEL", "INFO")
    log_channel_id: int = get_env("LOG_CHANNEL_ID", 0, cast=int)
    start_image: str = get_env("START_IMAGE", "")
    log_file: str = get_env("LOG_FILE", "bot.log")
    run_self_tests: bool = get_env("RUN_SELF_TESTS", False, cast=bool)
    port: int = get_env("PORT", 0, cast=int)

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
