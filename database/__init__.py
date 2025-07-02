from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client.get_default_database()

# Collections
approvals = db['approvals']  # {chat_id: [user_ids]}
biomode = db['biomode']      # {chat_id: bool}
