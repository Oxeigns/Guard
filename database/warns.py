from . import db

warns_col = db['warns']

async def add_warn(chat_id: int, user_id: int) -> int:
    data = await warns_col.find_one({"chat_id": chat_id, "user_id": user_id})
    count = data.get("count", 0) + 1 if data else 1
    await warns_col.update_one({"chat_id": chat_id, "user_id": user_id}, {"$set": {"count": count}}, upsert=True)
    return count

async def clear_warns(chat_id: int, user_id: int):
    await warns_col.delete_one({"chat_id": chat_id, "user_id": user_id})

async def get_warns(chat_id: int, user_id: int) -> int:
    data = await warns_col.find_one({"chat_id": chat_id, "user_id": user_id})
    return data.get("count", 0) if data else 0
