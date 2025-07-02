from . import db
import os

blacklist_col = db['blacklists']
BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'blacklists')
os.makedirs(BASE_DIR, exist_ok=True)

async def add_word(chat_id: int, word: str):
    await blacklist_col.update_one({'chat_id': chat_id}, {'$addToSet': {'words': word.lower()}}, upsert=True)
    await sync_words(chat_id)

async def remove_word(chat_id: int, word: str):
    await blacklist_col.update_one({'chat_id': chat_id}, {'$pull': {'words': word.lower()}}, upsert=True)
    await sync_words(chat_id)

async def list_words(chat_id: int) -> list:
    data = await blacklist_col.find_one({'chat_id': chat_id})
    return data.get('words', []) if data else []

async def sync_words(chat_id: int) -> str:
    words = await list_words(chat_id)
    path = os.path.join(BASE_DIR, f"{chat_id}.txt")
    with open(path, 'w') as f:
        f.write('\n'.join(words))
    return path
