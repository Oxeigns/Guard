from . import db

welcome_col = db['welcome']

DEFAULT_WELCOME = 'Welcome {mention}!'
DEFAULT_GOODBYE = 'Goodbye {mention}!'

async def set_welcome(chat_id: int, text: str):
    await welcome_col.update_one({'chat_id': chat_id}, {'$set': {'text': text}}, upsert=True)

async def get_welcome(chat_id: int) -> str:
    data = await welcome_col.find_one({'chat_id': chat_id})
    return data.get('text', DEFAULT_WELCOME)

async def set_goodbye(chat_id: int, text: str):
    await welcome_col.update_one({'chat_id': chat_id}, {'$set': {'goodbye': text}}, upsert=True)

async def get_goodbye(chat_id: int) -> str:
    data = await welcome_col.find_one({'chat_id': chat_id})
    return data.get('goodbye', DEFAULT_GOODBYE)
