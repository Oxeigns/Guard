from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from utils.filters import admin_filter
from database.approvals import add_approval, remove_approval
from utils.logger import log_to_channel


async def approve(client: Client, message):
    if not message.reply_to_message:
        return await message.reply("Reply to a user to approve")
    user_id = message.reply_to_message.from_user.id
    await add_approval(message.chat.id, user_id)
    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Disapprove", callback_data=f"disapprove:{user_id}")]]
    )
    await message.reply("User approved", reply_markup=buttons)
    await log_to_channel(client, f"Approved {user_id} in {message.chat.id}")

async def disapprove(client: Client, message):
    if not message.reply_to_message:
        return await message.reply("Reply to a user to disapprove")
    user_id = message.reply_to_message.from_user.id
    await remove_approval(message.chat.id, user_id)
    await message.reply("User disapproved")
    await log_to_channel(client, f"Disapproved {user_id} in {message.chat.id}")


async def disapprove_callback(client: Client, callback_query):
    data = callback_query.data.split(":")
    user_id = int(data[1])
    await remove_approval(callback_query.message.chat.id, user_id)
    await callback_query.answer("User disapproved", show_alert=True)
    await callback_query.message.edit("User disapproved")
    await log_to_channel(client, f"Disapproved {user_id} via button in {callback_query.message.chat.id}")


def register(app: Client):
    app.add_handler(MessageHandler(approve, filters.command("approve") & admin_filter))
    app.add_handler(MessageHandler(disapprove, filters.command("disapprove") & admin_filter))
    app.add_handler(CallbackQueryHandler(disapprove_callback, filters.regex("^disapprove:")))
