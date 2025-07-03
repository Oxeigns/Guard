from typing import Dict

from . import db

warnings_col = db["bio_warnings"]


async def add_warning(chat_id: int, user_id: int) -> int:
    field = f"warnings.{user_id}"
    await warnings_col.update_one({"chat_id": chat_id}, {"$inc": {field: 1}}, upsert=True)
    data = await warnings_col.find_one({"chat_id": chat_id})
    return int(data.get("warnings", {}).get(str(user_id), 0))


async def clear_warnings(chat_id: int, user_id: int) -> None:
    field = f"warnings.{user_id}"
    await warnings_col.update_one({"chat_id": chat_id}, {"$unset": {field: ""}}, upsert=True)


async def get_warnings(chat_id: int, user_id: int) -> int:
    data = await warnings_col.find_one({"chat_id": chat_id})
    return int(data.get("warnings", {}).get(str(user_id), 0)) if data else 0


async def get_all_warnings(chat_id: int) -> Dict[int, int]:
    data = await warnings_col.find_one({"chat_id": chat_id})
    if not data:
        return {}
    return {int(uid): int(count) for uid, count in data.get("warnings", {}).items()}

