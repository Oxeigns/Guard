from . import db

biomode_col = db['biomode']

async def set_biomode(chat_id: int, enabled: bool):
    await biomode_col.update_one({"chat_id": chat_id}, {"$set": {"enabled": enabled}}, upsert=True)

async def is_biomode(chat_id: int) -> bool:
    data = await biomode_col.find_one({"chat_id": chat_id})
    return bool(data and data.get("enabled", False))
