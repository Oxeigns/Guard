from pyrogram import Client, filters
from utils.filters import admin_filter
from database import approvals


async def approve(client: Client, message):
    if not message.reply_to_message:
        return await message.reply("Reply to a user to approve")
    user_id = message.reply_to_message.from_user.id
    approvals.update_one({"chat_id": message.chat.id}, {"$addToSet": {"user_ids": user_id}}, upsert=True)
    await message.reply("User approved")

async def disapprove(client: Client, message):
    if not message.reply_to_message:
        return await message.reply("Reply to a user to disapprove")
    user_id = message.reply_to_message.from_user.id
    approvals.update_one({"chat_id": message.chat.id}, {"$pull": {"user_ids": user_id}}, upsert=True)
    await message.reply("User disapproved")


def register(app: Client):
    app.add_handler(filters.command("approve") & admin_filter, approve)
    app.add_handler(filters.command("disapprove") & admin_filter, disapprove)
