from . import db

autodelete_col = db['autodelete']

async def set_autodelete(chat_id: int, seconds: int):
    await autodelete_col.update_one({'chat_id': chat_id}, {'$set': {'seconds': seconds}}, upsert=True)

async def get_autodelete(chat_id: int) -> int:
    data = await autodelete_col.find_one({'chat_id': chat_id})
    return int(data.get('seconds', 0)) if data else 0
