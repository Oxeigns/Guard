client = None
main = None

async def get_warnings(chat_id, user_id):
    doc = await main.warnings.find_one({"chat_id": chat_id, "user_id": user_id})
    return doc["count"] if doc else 0

async def increment_warning(chat_id, user_id):
    current = await get_warnings(chat_id, user_id)
    if current >= 3:
        return current
    await main.warnings.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"chat_id": chat_id, "user_id": user_id}, "$inc": {"count": 1}},
        upsert=True
    )
    return current + 1

async def reset_warning(chat_id, user_id):
    await main.warnings.delete_one({"chat_id": chat_id, "user_id": user_id})

async def is_approved(chat_id, user_id):
    doc = await main.approved.find_one({"chat_id": chat_id})
    return user_id in doc.get("users", []) if doc else False

async def approve_user(chat_id, user_id):
    await main.approved.update_one(
        {"chat_id": chat_id},
        {"$addToSet": {"users": user_id}},
        upsert=True
    )

async def unapprove_user(chat_id, user_id):
    await main.approved.update_one(
        {"chat_id": chat_id},
        {"$pull": {"users": user_id}},
        upsert=True
    )

async def get_approved(chat_id):
    doc = await main.approved.find_one({"chat_id": chat_id})
    return doc.get("users", []) if doc else []

async def get_autodelete(chat_id):
    doc = await main.autodelete.find_one({"chat_id": chat_id})
    return doc["delay"] if doc else 0

async def set_autodelete(chat_id, seconds):
    await main.autodelete.update_one(
        {"chat_id": chat_id},
        {"$set": {"delay": seconds}},
        upsert=True
    )

async def get_bio_filter(chat_id):
    doc = await main.settings.find_one({"chat_id": chat_id})
    return doc.get("bio_filter", True) if doc else True

async def toggle_bio_filter(chat_id):
    current = await get_bio_filter(chat_id)
    await main.settings.update_one(
        {"chat_id": chat_id},
        {"$set": {"bio_filter": not current}},
        upsert=True
    )
    return not current
