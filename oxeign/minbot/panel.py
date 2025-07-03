from typing import Dict, Tuple
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.enums import ParseMode

from oxeign.swagger.biomode import is_biomode, set_biomode
from oxeign.swagger.autodelete import get_autodelete, set_autodelete
from oxeign.swagger.approvals import add_approval, remove_approval, approvals_col
from oxeign.utils.perms import is_admin

pending_actions: Dict[Tuple[int, int], str] = {}


async def build_panel(chat_id: int) -> InlineKeyboardMarkup:
    biomode = await is_biomode(chat_id)
    autodel = await get_autodelete(chat_id)
    rows = [
        [InlineKeyboardButton(
            f"🛡 Bio Link Filter {'On' if biomode else 'Off'}",
            callback_data="toggle_biolink",
        )],
        [InlineKeyboardButton(
            f"⏱ Set AutoDelete ({autodel if autodel else 'Off'})",
            callback_data="autodelete",
        )],
        [
            InlineKeyboardButton("✅ Approve User", callback_data="approve_user"),
            InlineKeyboardButton("❌ Unapprove User", callback_data="unapprove_user"),
        ],
        [InlineKeyboardButton("📋 View Approved", callback_data="view_approved")],
        [InlineKeyboardButton("Close", callback_data="close")],
    ]
    return InlineKeyboardMarkup(rows)


async def toggle_biolink_cb(client: Client, callback_query):
    if not await is_admin(client, callback_query.message.chat.id, callback_query.from_user.id):
        return await callback_query.answer("Admins only", show_alert=True)
    enabled = not await is_biomode(callback_query.message.chat.id)
    await set_biomode(callback_query.message.chat.id, enabled)
    await callback_query.answer("Updated", show_alert=False)
    markup = await build_panel(callback_query.message.chat.id)
    await callback_query.message.edit("**Control Panel**", reply_markup=markup, parse_mode=ParseMode.MARKDOWN)


async def autodelete_cb(client: Client, callback_query):
    if not await is_admin(client, callback_query.message.chat.id, callback_query.from_user.id):
        return await callback_query.answer("Admins only", show_alert=True)
    pending_actions[(callback_query.message.chat.id, callback_query.from_user.id)] = "autodel"
    await callback_query.answer()
    await callback_query.message.reply("Send auto-delete delay in seconds (0 to disable).")


async def approve_user_cb(client: Client, callback_query):
    if not await is_admin(client, callback_query.message.chat.id, callback_query.from_user.id):
        return await callback_query.answer("Admins only", show_alert=True)
    pending_actions[(callback_query.message.chat.id, callback_query.from_user.id)] = "approve"
    await callback_query.answer()
    await callback_query.message.reply("Reply to the user's message to approve.")


async def unapprove_user_cb(client: Client, callback_query):
    if not await is_admin(client, callback_query.message.chat.id, callback_query.from_user.id):
        return await callback_query.answer("Admins only", show_alert=True)
    pending_actions[(callback_query.message.chat.id, callback_query.from_user.id)] = "unapprove"
    await callback_query.answer()
    await callback_query.message.reply("Reply to the user's message to unapprove.")


async def view_approved_cb(client: Client, callback_query):
    if not await is_admin(client, callback_query.message.chat.id, callback_query.from_user.id):
        return await callback_query.answer("Admins only", show_alert=True)
    doc = await approvals_col.find_one({"chat_id": callback_query.message.chat.id})
    users = doc.get("user_ids", []) if doc else []
    if users:
        lines = [f"- [User](tg://user?id={uid})" for uid in users]
        text = "**Approved Users:**\n" + "\n".join(lines)
    else:
        text = "No approved users."
    markup = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back")]])
    await callback_query.message.edit(text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)


async def back_cb(client: Client, callback_query):
    markup = await build_panel(callback_query.message.chat.id)
    await callback_query.message.edit("**Control Panel**", reply_markup=markup, parse_mode=ParseMode.MARKDOWN)


async def close_cb(client: Client, callback_query):
    await callback_query.message.delete()


async def handle_pending(client: Client, message: Message):
    key = (message.chat.id, message.from_user.id)
    if key not in pending_actions:
        return
    action = pending_actions.pop(key)
    if action in ("approve", "unapprove"):
        if not message.reply_to_message:
            return
        target_id = message.reply_to_message.from_user.id
        if action == "approve":
            await add_approval(message.chat.id, target_id)
            await message.reply(f"Approved [user](tg://user?id={target_id})", parse_mode=ParseMode.MARKDOWN)
        else:
            await remove_approval(message.chat.id, target_id)
            await message.reply(f"Unapproved [user](tg://user?id={target_id})", parse_mode=ParseMode.MARKDOWN)
    elif action == "autodel":
        try:
            seconds = int(message.text)
            if seconds < 0:
                raise ValueError
        except Exception:
            return await message.reply("Send a non-negative number.")
        await set_autodelete(message.chat.id, seconds)
        if seconds:
            await message.reply(f"Auto-delete set to {seconds}s", parse_mode=ParseMode.MARKDOWN)
        else:
            await message.reply("Auto-delete disabled", parse_mode=ParseMode.MARKDOWN)


def register(app: Client):
    app.add_handler(MessageHandler(handle_pending, filters.group), group=2)
    app.add_handler(CallbackQueryHandler(toggle_biolink_cb, filters.regex("^toggle_biolink$")))
    app.add_handler(CallbackQueryHandler(autodelete_cb, filters.regex("^autodelete$")))
    app.add_handler(CallbackQueryHandler(approve_user_cb, filters.regex("^approve_user$")))
    app.add_handler(CallbackQueryHandler(unapprove_user_cb, filters.regex("^unapprove_user$")))
    app.add_handler(CallbackQueryHandler(view_approved_cb, filters.regex("^view_approved$")))
    app.add_handler(CallbackQueryHandler(back_cb, filters.regex("^back$")))
    app.add_handler(CallbackQueryHandler(close_cb, filters.regex("^close$")))
