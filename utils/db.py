from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, MONGO_DB

_client = AsyncIOMotorClient(MONGO_URI)
_db = _client[MONGO_DB]


def get_db():
    return _db


# ------------------ SETTINGS: linkfilter, editmode, etc ------------------ #
async def get_setting(chat_id: int, key: str, default: str | None = None) -> str | None:
    doc = await _db.kv_settings.find_one({"chat_id": chat_id, "key": key})
    return doc.get("value") if doc else default


async def set_setting(chat_id: int, key: str, value: str) -> None:
    await _db.kv_settings.update_one(
        {"chat_id": chat_id, "key": key},
        {"$set": {"value": value}},
        upsert=True,
    )


# ------------------ BIO FILTER ------------------ #
async def get_bio_filter(chat_id: int) -> bool:
    value = await get_setting(chat_id, "biofilter", "0")
    return value == "1"


async def set_bio_filter(chat_id: int, enabled: bool) -> None:
    await set_setting(chat_id, "biofilter", "1" if enabled else "0")


# ------------------ APPROVAL ------------------ #
async def approve_user(chat_id: int, user_id: int) -> None:
    await _db.approved_users.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"approved": True}},
        upsert=True,
    )


async def unapprove_user(chat_id: int, user_id: int) -> None:
    await _db.approved_users.delete_one({"chat_id": chat_id, "user_id": user_id})


async def is_approved(chat_id: int, user_id: int) -> bool:
    return await _db.approved_users.find_one({"chat_id": chat_id, "user_id": user_id}) is not None


async def get_approved(chat_id: int) -> list[int]:
    cursor = _db.approved_users.find({"chat_id": chat_id})
    return [doc["user_id"] async for doc in cursor]


async def set_approval_mode(chat_id: int, enabled: bool) -> None:
    await set_setting(chat_id, "approval_mode", "1" if enabled else "0")


async def get_approval_mode(chat_id: int) -> bool:
    value = await get_setting(chat_id, "approval_mode", "0")
    return value == "1"


async def toggle_approval_mode(chat_id: int) -> bool:
    """Flip the approval mode for the given chat and return the new state."""
    current = await get_approval_mode(chat_id)
    await set_approval_mode(chat_id, not current)
    return not current


# ------------------ WARNINGS ------------------ #
async def increment_warning(chat_id: int, user_id: int) -> int:
    doc = await _db.warnings.find_one_and_update(
        {"chat_id": chat_id, "user_id": user_id},
        {"$inc": {"count": 1}},
        upsert=True,
        return_document=True,
    )
    return doc["count"]


async def reset_warning(chat_id: int, user_id: int) -> None:
    await _db.warnings.delete_one({"chat_id": chat_id, "user_id": user_id})


# ------------------ BROADCAST STORAGE ------------------ #
async def add_broadcast_user(user_id: int) -> None:
    """Store a user ID for future broadcasts."""
    await _db.broadcast_users.update_one({"_id": user_id}, {"$set": {}}, upsert=True)


async def add_broadcast_group(chat_id: int) -> None:
    """Store a group ID for future broadcasts."""
    await _db.broadcast_groups.update_one({"_id": chat_id}, {"$set": {}}, upsert=True)


async def remove_broadcast_group(chat_id: int) -> None:
    await _db.broadcast_groups.delete_one({"_id": chat_id})


async def get_broadcast_users() -> list[int]:
    cursor = _db.broadcast_users.find()
    return [doc["_id"] async for doc in cursor]


async def get_broadcast_groups() -> list[int]:
    cursor = _db.broadcast_groups.find()
    return [doc["_id"] async for doc in cursor]


# ------------------ DB LIFECYCLE ------------------ #
async def init_db(uri: str, db_name: str):
    """Initialize MongoDB client with URI and database name."""
    global _client, _db
    _client = AsyncIOMotorClient(uri)
    _db = _client[db_name]


async def close_db():
    """Gracefully close the MongoDB connection."""
    _client.close()
