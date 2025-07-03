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

# Keeps track of admins waiting to reply with a user for approve/unapprove
pending_actions: Dict[Tuple[int, int], str] = {}


async def build_start_panel(client: Client) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("📖 Help & Commands", callback_data="menu:main")],
        [
            InlineKeyboardButton("📣 Support Channel", callback_data="menu:support"),
            InlineKeyboardButton("👨‍💻 Developer", callback_data="menu:developer"),
        ],
    ]
    return InlineKeyboardMarkup(rows)


async def build_private_panel(client: Client) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                "➕ Add to Group",
                url=f"https://t.me/{client.me.username}?startgroup=true",
            )
        ],
        [InlineKeyboardButton("📖 Help & Commands", callback_data="menu:main")],
        [InlineKeyboardButton("👨‍💻 Developer", callback_data="menu:developer")],
    ]
    return InlineKeyboardMarkup(rows)


async def build_main_panel(client: Client, private: bool = False) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("🛡️ Bio Link Settings", callback_data="menu:bio")],
        [InlineKeyboardButton("🕒 AutoDelete Settings", callback_data="menu:autodel")],
        [
            InlineKeyboardButton("✅ Approve User", callback_data="approve_user"),
            InlineKeyboardButton("❌ Unapprove User", callback_data="unapprove_user"),
        ],
        [InlineKeyboardButton("📋 View Approved", callback_data="view_approved")],
        [
            InlineKeyboardButton("📣 Support Channel", callback_data="menu:support"),
            InlineKeyboardButton("👨‍💻 Developer", callback_data="menu:developer"),
        ],
        [InlineKeyboardButton("❎ Close Panel", callback_data="close")],
    ]
    return InlineKeyboardMarkup(rows)


async def bio_panel(chat_id: int) -> tuple[str, InlineKeyboardMarkup]:
    enabled = await is_biomode(chat_id)
    status = "ON" if enabled else "OFF"
    rows = [
        [
            InlineKeyboardButton("🔘 Turn On", callback_data="bio:on"),
            InlineKeyboardButton("🔴 Turn Off", callback_data="bio:off"),
        ],
        [InlineKeyboardButton("🔙 Back to Control Panel", callback_data="menu:main")],
    ]
    return f"🛡 Bio Link Filter: {status}", InlineKeyboardMarkup(rows)


def approve_panel() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("✅ Approve", callback_data="approve_user"),
            InlineKeyboardButton("❌ Unapprove", callback_data="unapprove_user"),
        ],
        [
            InlineKeyboardButton("📋 List", callback_data="view_approved"),
            InlineKeyboardButton("🔙 Back", callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(rows)


def autodelete_panel() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("⏱️ Enable", callback_data="set_autodel:60"),
            InlineKeyboardButton("❌ Disable", callback_data="set_autodel:0"),
        ],
        [InlineKeyboardButton("🔙 Back to Control Panel", callback_data="menu:main")],
    ]
    return InlineKeyboardMarkup(rows)


async def panel_cmd(client: Client, message: Message):
    await send_panel(client, message)


async def send_panel(
    client: Client, message: Message, private: bool | None = None, start: bool = False
):
    if private is None:
        private = message.chat.type == "private"

    if start:
        markup = (
            await build_private_panel(client)
            if private
            else await build_start_panel(client)
        )
    else:
        markup = await build_main_panel(client, private=private)

    if not private:
        await message.reply_photo(
            PANEL_HEADER_URL,
            caption="**Control Panel**",
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await message.reply(
            "**Control Panel**",
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN,
        )


async def menu_router(client: Client, callback_query):
    data = callback_query.data.split(":", 1)[1]
    chat_id = callback_query.message.chat.id
    if data == "main":
        markup = await build_main_panel(
            client, private=callback_query.message.chat.type == "private"
        )
        text = "**Control Panel**"
    elif data == "bio":
        text, markup = await bio_panel(chat_id)
    elif data == "approve":
        markup = approve_panel()
        text = "**Approve System**"
    elif data == "autodel":
        markup = autodelete_panel()
        text = "**Auto Delete**"
    elif data == "support":
        markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📣 Open Channel", url=SUPPORT_LINK)],
                [InlineKeyboardButton("🔙 Back", callback_data="menu:main")],
            ]
        )
        text = "**Support**"
    elif data == "developer":
        markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("👨‍💻 Developer", url=DEV_LINK)],
                [InlineKeyboardButton("🔙 Back", callback_data="menu:main")],
            ]
        )
        text = "**Developer**"
    else:
        return
    await callback_query.message.edit(
        text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN
    )
    await callback_query.answer()


async def toggle_bio(client: Client, callback_query):
    if not await is_admin(
        client, callback_query.message.chat.id, callback_query.from_user.id
    ):
        return await callback_query.answer("Admins only", show_alert=True)
    enable = callback_query.data.endswith("on")
    await set_biomode(callback_query.message.chat.id, enable)
    await callback_query.answer("Updated", show_alert=False)
    text, markup = await bio_panel(callback_query.message.chat.id)
    await callback_query.message.edit(
        text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN
    )


async def set_autodel_cb(client: Client, callback_query):
    if not await is_admin(
        client, callback_query.message.chat.id, callback_query.from_user.id
    ):
        return await callback_query.answer("Admins only", show_alert=True)
    seconds = int(callback_query.data.split(":")[1])
    await set_autodelete(callback_query.message.chat.id, seconds)
    await callback_query.answer("Updated", show_alert=False)
    markup = autodelete_panel()
    await callback_query.message.edit(
        "**Auto Delete**", reply_markup=markup, parse_mode=ParseMode.MARKDOWN
    )


async def approve_user_cb(client: Client, callback_query):
    if not await is_admin(
        client, callback_query.message.chat.id, callback_query.from_user.id
    ):
        return await callback_query.answer("Admins only", show_alert=True)
    pending_actions[(callback_query.message.chat.id, callback_query.from_user.id)] = (
        "approve"
    )
    await callback_query.answer()
    await callback_query.message.reply(
        "Reply to the user's message in this chat to approve them."
    )


async def unapprove_user_cb(client: Client, callback_query):
    if not await is_admin(
        client, callback_query.message.chat.id, callback_query.from_user.id
    ):
        return await callback_query.answer("Admins only", show_alert=True)
    pending_actions[(callback_query.message.chat.id, callback_query.from_user.id)] = (
        "unapprove"
    )
    await callback_query.answer()
    await callback_query.message.reply(
        "Reply to the user's message in this chat to unapprove them."
    )


async def view_approved_cb(client: Client, callback_query):
    if not await is_admin(
        client, callback_query.message.chat.id, callback_query.from_user.id
    ):
        return await callback_query.answer("Admins only", show_alert=True)
    doc = await approvals_col.find_one({"chat_id": callback_query.message.chat.id})
    users = doc.get("user_ids", []) if doc else []
    if users:
        lines = [f"- [User](tg://user?id={uid})" for uid in users]
        text = "**Approved Users:**\n" + "\n".join(lines)
    else:
        text = "No approved users."
    markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔙 Back", callback_data="menu:approve")]]
    )
    await callback_query.message.edit(
        text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN
    )


async def handle_pending(client: Client, message: Message):
    key = (message.chat.id, message.from_user.id)
    if key not in pending_actions or not message.reply_to_message:
        return
    action = pending_actions.pop(key)
    target_id = message.reply_to_message.from_user.id
    if action == "approve":
        await add_approval(message.chat.id, target_id)
        await message.reply(
            f"Approved [user](tg://user?id={target_id})", parse_mode=ParseMode.MARKDOWN
        )
    else:
        await remove_approval(message.chat.id, target_id)
        await message.reply(
            f"Unapproved [user](tg://user?id={target_id})",
            parse_mode=ParseMode.MARKDOWN,
        )


async def close_cb(client: Client, callback_query):
    await callback_query.message.delete()


def register(app: Client):
    app.add_handler(
        MessageHandler(
            panel_cmd, filters.command(["panel", "help", "menu"]) & filters.group
        )
    )
    app.add_handler(MessageHandler(handle_pending, filters.group), group=2)
    app.add_handler(CallbackQueryHandler(menu_router, filters.regex(r"^menu:")))
    app.add_handler(CallbackQueryHandler(toggle_bio, filters.regex(r"^bio:")))
    app.add_handler(
        CallbackQueryHandler(set_autodel_cb, filters.regex(r"^set_autodel:"))
    )
    app.add_handler(
        CallbackQueryHandler(approve_user_cb, filters.regex(r"^approve_user$"))
    )
    app.add_handler(
        CallbackQueryHandler(unapprove_user_cb, filters.regex(r"^unapprove_user$"))
    )
    app.add_handler(
        CallbackQueryHandler(view_approved_cb, filters.regex(r"^view_approved$"))
    )
    app.add_handler(CallbackQueryHandler(close_cb, filters.regex(r"^close$")))
