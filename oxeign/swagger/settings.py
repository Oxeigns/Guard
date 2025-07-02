from . import db

settings_col = db['settings']

DEFAULTS = {
    "mode": "telegraph",
    "limit": 4000,
}

async def get_settings(chat_id: int) -> dict:
    data = await settings_col.find_one({"chat_id": chat_id})
    if not data:
        return DEFAULTS.copy()
    return {"mode": data.get("mode", DEFAULTS["mode"]), "limit": data.get("limit", DEFAULTS["limit"])}

async def set_mode(chat_id: int, mode: str):
    await settings_col.update_one({"chat_id": chat_id}, {"$set": {"mode": mode}}, upsert=True)

async def set_limit(chat_id: int, limit: int):
    await settings_col.update_one({"chat_id": chat_id}, {"$set": {"limit": limit}}, upsert=True)
