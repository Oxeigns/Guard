"""MongoDB utilities."""
import asyncio
import logging
from pymongo import MongoClient

logger = logging.getLogger(__name__)

_client: MongoClient | None = None
_db = None


def init_db(uri: str) -> None:
    """Initialize MongoDB connection."""
    global _client, _db
    _client = MongoClient(uri)
    _db = _client.get_default_database()
    _db.command("ping")
    _db.actions.create_index("chat_id")
    logger.info("MongoDB initialized")


async def close_db() -> None:
    if _client:
        _client.close()


async def log_action(chat_id: int, user_id: int, action: str) -> None:
    if not _db:
        return
    await asyncio.get_running_loop().run_in_executor(
        None,
        lambda: _db.actions.insert_one({
            "chat_id": chat_id,
            "user_id": user_id,
            "action": action,
        })
    )
