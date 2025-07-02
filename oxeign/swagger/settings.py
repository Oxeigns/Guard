from . import db

settings_col = db['settings']

DEFAULTS = {
    "mode": "telegraph",
    "limit": 4000,
    "anti_spam": False,
    "anti_flood": False,
    "captcha": False,
    "tag_all": True,
    "link_control": False,
    "media_filter": False,
    "night_mode": False,
}

async def get_settings(chat_id: int) -> dict:
    data = await settings_col.find_one({"chat_id": chat_id}) or {}
    result = DEFAULTS.copy()
    result.update({k: data.get(k, v) for k, v in DEFAULTS.items()})
    return result

async def set_mode(chat_id: int, mode: str):
    await settings_col.update_one({"chat_id": chat_id}, {"$set": {"mode": mode}}, upsert=True)

async def set_limit(chat_id: int, limit: int):
    await settings_col.update_one({"chat_id": chat_id}, {"$set": {"limit": limit}}, upsert=True)

async def set_setting(chat_id: int, key: str, value):
    await settings_col.update_one({"chat_id": chat_id}, {"$set": {key: value}}, upsert=True)

async def toggle_setting(chat_id: int, key: str) -> bool:
    settings = await get_settings(chat_id)
    new_val = not settings.get(key, False)
    await set_setting(chat_id, key, new_val)
    return new_val
