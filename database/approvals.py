from . import db

approvals_col = db['approvals']

async def add_approval(chat_id: int, user_id: int):
    await approvals_col.update_one({"chat_id": chat_id}, {"$addToSet": {"user_ids": user_id}}, upsert=True)

async def remove_approval(chat_id: int, user_id: int):
    await approvals_col.update_one({"chat_id": chat_id}, {"$pull": {"user_ids": user_id}}, upsert=True)

async def is_approved(chat_id: int, user_id: int) -> bool:
    data = await approvals_col.find_one({"chat_id": chat_id})
    return bool(data and user_id in data.get("user_ids", []))
