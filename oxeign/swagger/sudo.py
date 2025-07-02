from . import db

sudo_col = db["sudos"]

async def add_sudo(user_id: int):
    await sudo_col.update_one({"_id": 0}, {"$addToSet": {"user_ids": user_id}}, upsert=True)

async def remove_sudo(user_id: int):
    await sudo_col.update_one({"_id": 0}, {"$pull": {"user_ids": user_id}}, upsert=True)

async def get_sudos() -> list:
    data = await sudo_col.find_one({"_id": 0})
    return data.get("user_ids", []) if data else []
