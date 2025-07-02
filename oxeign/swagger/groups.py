from . import db

group_col = db['groups']

async def add_group(chat_id: int):
    await group_col.update_one({'_id': chat_id}, {'$set': {'_id': chat_id}}, upsert=True)

async def remove_group(chat_id: int):
    await group_col.delete_one({'_id': chat_id})

async def get_groups() -> list:
    cursor = group_col.find({}, {'_id': 1})
    return [doc['_id'] async for doc in cursor]
