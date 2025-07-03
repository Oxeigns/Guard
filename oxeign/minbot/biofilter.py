import re
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from oxeign.swagger.biomode import is_biomode
from oxeign.swagger.approvals import is_approved, add_approval
from oxeign.utils.perms import is_admin

# detect telegram usernames/links and general web links
LINK_RE = re.compile(r"(?:https?://|www\.|t\.me|telegram\.me|@)", re.I)


async def check_bio(client: Client, message: Message):
    if message.chat.type not in ("supergroup", "group"):
        return
    if not await is_biomode(message.chat.id):
        return
    if not message.from_user:
        return
    if await is_admin(client, message.chat.id, message.from_user.id):
        return
    if await is_approved(message.chat.id, message.from_user.id):
        return
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        bio = member.bio or ""
    except Exception:
        bio = ""
    if bio and LINK_RE.search(bio.lower()):
        try:
            await message.delete()
        except Exception:
            pass
        warn_text = f"{message.from_user.mention}, remove Telegram links from your bio."
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Approve", callback_data=f"approve:{message.from_user.id}"
                    )
                ]
            ]
        )
        await client.send_message(message.chat.id, warn_text, reply_markup=buttons)
        try:
            await client.send_message(
                message.from_user.id,
                "Please remove Telegram links from your bio to chat here.",
            )
        except Exception:
            pass


async def approve_callback(client: Client, callback_query):
    user_id = int(callback_query.data.split(":")[1])
    if not await is_admin(
        client, callback_query.message.chat.id, callback_query.from_user.id
    ):
        return await callback_query.answer("Admins only", show_alert=True)
    await add_approval(callback_query.message.chat.id, user_id)
    await callback_query.answer("User approved", show_alert=True)
    await callback_query.message.edit("User approved")


def register(app: Client):
    app.add_handler(MessageHandler(check_bio, filters.group & ~filters.service))
    app.add_handler(CallbackQueryHandler(approve_callback, filters.regex("^approve:")))
