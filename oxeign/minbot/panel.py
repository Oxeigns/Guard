from typing import Dict, Tuple
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.enums import ParseMode

from oxeign.swagger.biomode import is_biomode, set_biomode
from oxeign.swagger.autodelete import get_autodelete, set_autodelete
from oxeign.swagger.approvals import add_approval, remove_approval, approvals_col
from oxeign.utils.perms import is_admin
from oxeign.config import SUPPORT_LINK, DEV_LINK, PANEL_HEADER_URL

pending_actions: Dict[Tuple[int, int], str] = {}


async def build_panel(
    client: Client, chat_id: int, private: bool = False
) -> InlineKeyboardMarkup:
    if private:
        rows = [
            [
                InlineKeyboardButton(
                    "➕ Add to Group",
                    url=f"https://t.me/{client.me.username}?startgroup=true",
                )
            ],
            [
                InlineKeyboardButton("📣 Support", url=SUPPORT_LINK),
                InlineKeyboardButton("👨‍💻 Developer", url=DEV_LINK),
            ],
        ]
        return InlineKeyboardMarkup(rows)

    biomode = await is_biomode(chat_id)
    autodel = await get_autodelete(chat_id)
    rows = [
        [
            InlineKeyboardButton(
                f"🛡 Bio Link Filter {'On' if biomode else 'Off'}",
                callback_data="toggle_biolink",
            )
        ],
        [
            InlineKeyboardButton(
                f"⏱ AutoDelete ({autodel if autodel else 'Off'})",
                callback_data="autodelete",
            )
        ],
        [
            InlineKeyboardButton("✅ Approve", callback_data="approve_user"),
            InlineKeyboardButton("❌ Unapprove", callback_data="unapprove_user"),
        ],
        [
            InlineKeyboardButton("📋 Approved", callback_data="view_approved"),
            InlineKeyboardButton("Close", callback_data="close"),
        ],
        [
            InlineKeyboardButton("📣 Support", url=SUPPORT_LINK),
            InlineKeyboardButton("👨‍💻 Developer", url=DEV_LINK),
        ],
    ]
    return InlineKeyboardMarkup(rows)


async def panel_cmd(client: Client, message: Message):
    await send_panel(client, message)


async def send_panel(client: Client, message: Message):
    private = message.chat.type == "private"
    markup = await build_panel(client, message.chat.id, private=private)
    await message.reply_photo(
        PANEL_HEADER_URL,
        caption="**Control Panel**",
        reply_markup=markup,
        parse_mode=ParseMode.MARKDOWN,
    )


async def toggle_biolink_cb(client: Client, callback_query):
    if not await is_admin(client, callback_query.message.chat.id, callback_query.from_user.id):
        return await callback_query.answer("Admins only", show_alert=True)
    enabled = not await is_biomode(callback_query.message.chat.id)
    await set_biomode(callback_query.message.chat.id, enabled)
    await callback_query.answer("Updated", show_alert=False)
    markup = await build_panel(client, callback_query.message.chat.id, private=callback_query.message.chat.type == "private")
    await callback_query.message.edit("**Control Panel**", reply_markup=markup, parse_mode=ParseMode.MARKDOWN)


autodel_menu = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("10s", callback_data="set_autodel:10"),
            InlineKeyboardButton("30s", callback_data="set_autodel:30"),
            InlineKeyboardButton("1m", callback_data="set_autodel:60"),
        ],
        [
            InlineKeyboardButton("2m", callback_data="set_autodel:120"),
            InlineKeyboardButton("5m", callback_data="set_autodel:300"),
            InlineKeyboardButton("10m", callback_data="set_autodel:600"),
        ],
        [
            InlineKeyboardButton("3h", callback_data="set_autodel:10800"),
            InlineKeyboardButton("6h", callback_data="set_autodel:21600"),
            InlineKeyboardButton("12h", callback_data="set_autodel:43200"),
        ],
        [
            InlineKeyboardButton("24h", callback_data="set_autodel:86400"),
            InlineKeyboardButton("Off", callback_data="set_autodel:0"),
        ],
        [InlineKeyboardButton("⬅️ Back", callback_data="back")],
    ]
)


async def autodelete_cb(client: Client, callback_query):
    if not await is_admin(client, callback_query.message.chat.id, callback_query.from_user.id):
        return await callback_query.answer("Admins only", show_alert=True)
    await callback_query.message.edit(
        "**Select auto-delete delay:**",
        reply_markup=autodel_menu,
        parse_mode=ParseMode.MARKDOWN,
    )


async def set_autodel_cb(client: Client, callback_query):
    if not await is_admin(client, callback_query.message.chat.id, callback_query.from_user.id):
        return await callback_query.answer("Admins only", show_alert=True)
    seconds = int(callback_query.data.split(":")[1])
    await set_autodelete(callback_query.message.chat.id, seconds)
    await callback_query.answer("Updated", show_alert=False)
    markup = await build_panel(client, callback_query.message.chat.id, private=callback_query.message.chat.type == "private")
    await callback_query.message.edit("**Control Panel**", reply_markup=markup, parse_mode=ParseMode.MARKDOWN)


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
    markup = await build_panel(client, callback_query.message.chat.id, private=callback_query.message.chat.type == "private")
    await callback_query.message.edit("**Control Panel**", reply_markup=markup, parse_mode=ParseMode.MARKDOWN)


async def close_cb(client: Client, callback_query):
    await callback_query.message.delete()


async def handle_pending(client: Client, message: Message):
    key = (message.chat.id, message.from_user.id)
    if key not in pending_actions or not message.reply_to_message:
        return
    action = pending_actions.pop(key)
    target_id = message.reply_to_message.from_user.id
    if action == "approve":
        await add_approval(message.chat.id, target_id)
        await message.reply(f"Approved [user](tg://user?id={target_id})", parse_mode=ParseMode.MARKDOWN)
    else:
        await remove_approval(message.chat.id, target_id)
        await message.reply(f"Unapproved [user](tg://user?id={target_id})", parse_mode=ParseMode.MARKDOWN)


def register(app: Client):
    app.add_handler(MessageHandler(panel_cmd, filters.command(["panel", "like"])))
    app.add_handler(MessageHandler(handle_pending, filters.group), group=2)
    app.add_handler(CallbackQueryHandler(toggle_biolink_cb, filters.regex("^toggle_biolink$")))
    app.add_handler(CallbackQueryHandler(autodelete_cb, filters.regex("^autodelete$")))
    app.add_handler(CallbackQueryHandler(set_autodel_cb, filters.regex("^set_autodel:")))
    app.add_handler(CallbackQueryHandler(approve_user_cb, filters.regex("^approve_user$")))
    app.add_handler(CallbackQueryHandler(unapprove_user_cb, filters.regex("^unapprove_user$")))
    app.add_handler(CallbackQueryHandler(view_approved_cb, filters.regex("^view_approved$")))
    app.add_handler(CallbackQueryHandler(back_cb, filters.regex("^back$")))
    app.add_handler(CallbackQueryHandler(close_cb, filters.regex("^close$")))
