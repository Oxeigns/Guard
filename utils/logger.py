import logging
from config import LOG_LEVEL, LOG_CHANNEL_ID


logging.basicConfig(level=getattr(logging, LOG_LEVEL))


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


async def log_to_channel(client, text: str):
    if LOG_CHANNEL_ID:
        try:
            await client.send_message(LOG_CHANNEL_ID, text)
        except Exception:
            pass
