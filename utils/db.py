from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI

_client = AsyncIOMotorClient(MONGO_URI)
_db = _client["telegram_bot"]  # use your actual DB name here


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
async def get_bio_filter(chat
