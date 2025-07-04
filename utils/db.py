"""Async MongoDB storage utilities for Guard."""

from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ReturnDocument

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


async def init_db(uri: str, name: str) -> None:
    """Initialise the MongoDB database and ensure indexes."""
    global _client, _db
    _client = AsyncIOMotorClient(uri)
    _db = _client[name]
    await _db.warnings.create_index([("chat_id", 1), ("user_id", 1)], unique=True)
    await _db.approved.create_index([("chat_id", 1), ("user_id", 1)], unique=True)
    await _db.settings.create_index("chat_id", unique=True)
    await _db.kv_settings.create_index([("chat_id", 1), ("key", 1)], unique=True)


def get_db() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("Database not initialised")
    return _db


async def close_db() -> None:
    if _client:
        _client.close()


async def get_warnings(chat_id: int, user_id: int) -> int:
    doc = await get_db().warnings.find_one({"chat_id": chat_id, "user_id": user_id})
    return int(doc.get("count", 0)) if doc else 0


async def increment_warning(chat_id: int, user_id: int) -> int:
    res = await get_db().warnings.find_one_and_update(
        {"chat_id": chat_id, "user_id": user_id},
        {"$inc": {"count": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    count = int(res.get("count", 0))
    return count


async def reset_warning(chat_id: int, user_id: int) -> None:
    await get_db().warnings.delete_one({"chat_id": chat_id, "user_id": user_id})


async def is_approved(chat_id: int, user_id: int) -> bool:
    doc = await get_db().approved.find_one({"chat_id": chat_id, "user_id": user_id})
    return doc is not None


async def approve_user(chat_id: int, user_id: int) -> None:
    await get_db().approved.update_one(
        {"chat_id": chat_id, "user_id": user_id}, {"$setOnInsert": {}}, upsert=True
    )


async def unapprove_user(chat_id: int, user_id: int) -> None:
    await get_db().approved.delete_one({"chat_id": chat_id, "user_id": user_id})


async def get_approved(chat_id: int) -> list[int]:
    cursor = get_db().approved.find({"chat_id": chat_id})
    return [doc["user_id"] async for doc in cursor]


async def get_autodelete(chat_id: int) -> int:
    doc = await get_db().settings.find_one({"chat_id": chat_id})
    return int(doc.get("autodelete", 0)) if doc else 0


async def set_autodelete(chat_id: int, seconds: int) -> None:
    await get_db().settings.update_one(
        {"chat_id": chat_id},
        {"$set": {"autodelete": seconds}},
        upsert=True,
    )


async def get_bio_filter(chat_id: int) -> bool:
    doc = await get_db().settings.find_one({"chat_id": chat_id})
    return bool(doc.get("bio_filter", True)) if doc else True


async def toggle_bio_filter(chat_id: int) -> bool:
    current = await get_bio_filter(chat_id)
    await set_bio_filter(chat_id, not current)
    return not current


async def set_bio_filter(chat_id: int, enabled: bool) -> None:
    await get_db().settings.update_one(
        {"chat_id": chat_id},
        {"$set": {"bio_filter": bool(enabled)}},
        upsert=True,
    )


async def get_approval_mode(chat_id: int) -> bool:
    doc = await get_db().settings.find_one({"chat_id": chat_id})
    return bool(doc.get("approval_mode", False)) if doc else False


async def set_approval_mode(chat_id: int, enabled: bool) -> None:
    await get_db().settings.update_one(
        {"chat_id": chat_id},
        {"$set": {"approval_mode": bool(enabled)}},
        upsert=True,
    )


async def toggle_approval_mode(chat_id: int) -> bool:
    current = await get_approval_mode(chat_id)
    await set_approval_mode(chat_id, not current)
    return not current


async def get_setting(chat_id: int, key: str, default: str | None = None) -> str | None:
    doc = await get_db().kv_settings.find_one({"chat_id": chat_id, "key": key})
    return doc.get("value") if doc else default


async def set_setting(chat_id: int, key: str, value: str) -> None:
    await get_db().kv_settings.update_one(
        {"chat_id": chat_id, "key": key},
        {"$set": {"value": value}},
        upsert=True,
    )


async def toggle_setting(chat_id: int, key: str, default: str = "0") -> str:
    current = await get_setting(chat_id, key, default)
    new_value = "1" if current == "0" else "0"
    await set_setting(chat_id, key, new_value)
    return new_value
