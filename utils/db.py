from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI

_client = AsyncIOMotorClient(MONGO_URI)
_db = _client["telegram_bot"]  # Use your DB name here


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
    doc = await _db.settings.find_one({"chat_id": chat_id})
    return bool(doc.get("bio_filter", True)) if doc else True


async def set_bio_filter(chat_id: int, enabled: bool) -> None:
    await _db.settings.update_one(
        {"chat_id": chat_id},
        {"$set": {"bio_filter": bool(enabled)}},
        upsert=True,
    )


# ------------------ APPROVAL MODE ------------------ #
async def get_approval_mode(chat_id: int) -> bool:
    doc = await _db.settings.find_one({"chat_id": chat_id})
    return bool(doc.get("approval_mode", False)) if doc else False


async def set_approval_mode(chat_id: int, enabled: bool) -> None:
    await _db.settings.update_one(
        {"chat_id": chat_id},
        {"$set": {"approval_mode": bool(enabled)}},
        upsert=True,
    )


async def toggle_approval_mode(chat_id: int) -> bool:
    current = await get_approval_mode(chat_id)
    new_state = not current
    await set_approval_mode(chat_id, new_state)
    return new_state


# ------------------ WARNINGS ------------------ #
async def increment_warning(chat_id: int, user_id: int) -> int:
    doc = await _db.warnings.find_one({"chat_id": chat_id, "user_id": user_id})
    count = doc.get("count", 0) + 1 if doc else 1
    await _db.warnings.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"count": count}},
        upsert=True,
    )
    return count


async def reset_warning(chat_id: int, user_id: int) -> None:
    await _db.warnings.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"count": 0}},
        upsert=True,
    )


# ------------------ APPROVED USERS ------------------ #
async def approve_user(chat_id: int, user_id: int) -> None:
    await _db.approved_users.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"approved": True}},
        upsert=True,
    )


async def unapprove_user(chat_id: int, user_id: int) -> None:
    await _db.approved_users.delete_one({"chat_id": chat_id, "user_id": user_id})


async def is_approved(chat_id: int, user_id: int) -> bool:
    doc = await _db.approved_users.find_one({"chat_id": chat_id, "user_id": user_id})
    return bool(doc)


async def get_approved(chat_id: int) -> list[int]:
    cursor = _db.approved_users.find({"chat_id": chat_id})
    return [doc["user_id"] async for doc in cursor]
