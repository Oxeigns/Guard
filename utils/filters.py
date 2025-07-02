from pyrogram import filters
from config import OWNER_ID, SUDO_USERS
from database import approvals, biomode

# Owner / sudo filters
owner_filter = filters.user(OWNER_ID)
sudo_filter = filters.user(SUDO_USERS)
admin_filter = owner_filter | sudo_filter

async def approved(user_id: int, chat_id: int) -> bool:
    data = approvals.find_one({"chat_id": chat_id})
    if not data:
        return False
    return user_id in data.get("user_ids", [])

async def is_biomode(chat_id: int) -> bool:
    data = biomode.find_one({"chat_id": chat_id})
    if not data:
        return False
    return data.get("enabled", False)
