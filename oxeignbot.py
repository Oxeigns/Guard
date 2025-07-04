# OxeignBot - Enhanced single-file Pyrogram bot

import asyncio
import logging
import os
import re
from contextlib import suppress

from pyrogram import Client, filters, idle
from pyrogram.enums import ParseMode, ChatType
from pyrogram.types import (
    CallbackQuery, InlineKeyboardButton,
    InlineKeyboardMarkup, Message, ChatPermissions
)
import aiosqlite
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
DB_PATH = os.getenv("DB_PATH", "oxeignbot.db")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger("OxeignBot")

if not all([API_ID, API_HASH, BOT_TOKEN]):
    raise RuntimeError("API_ID, API_HASH and BOT_TOKEN must be provided")

# ---------- Database ----------

db: aiosqlite.Connection | None = None

async def init_db(path: str) -> None:
    global db
    db = await aiosqlite.connect(path)
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            chat_id INTEGER,
            key TEXT,
            value TEXT,
            PRIMARY KEY(chat_id, key)
        )""")
    await db.execute("""
        CREATE TABLE IF NOT EXISTS group_meta (
            chat_id INTEGER PRIMARY KEY,
            title TEXT,
            owner_id INTEGER,
            photo_url TEXT
        )""")
    await db.commit()

async def set_setting(chat_id: int, key: str, value: str) -> None:
    await db.execute(
        "INSERT INTO settings(chat_id, key, value) VALUES(?,?,?) "
        "ON CONFLICT(chat_id, key) DO UPDATE SET value=excluded.value",
        (chat_id, key, value),
    )
    await db.commit()

async def get_setting(chat_id: int, key: str, default: str | None = None) -> str | None:
    cur = await db.execute("SELECT value FROM settings WHERE chat_id=? AND key=?", (chat_id, key))
    row = await cur.fetchone()
    await cur.close()
    return row[0] if row else default

async def toggle_setting(chat_id: int, key: str, default: str = "0") -> str:
    current = await get_setting(chat_id, key, default)
    new_value = "1" if current == "0" else "0"
    await set_setting(chat_id, key, new_value)
    return new_value

async def store_group_meta(chat_id: int, client: Client) -> None:
    chat = await client.get_chat(chat_id)
    owner_id = 0
    with suppress(Exception):
        async for m in client.get_chat_members(chat_id, filter="administrators"):
            if m.status == "creator":
                owner_id = m.user.id
                break
    photo_url = None
    with suppress(Exception):
        if chat.photo:
            photo_path = await client.download_media(chat.photo.big_file_id)
            photo_url = photo_path
    await db.execute(
        "INSERT OR REPLACE INTO group_meta(chat_id, title, owner_id, photo_url) VALUES(?,?,?,?)",
        (chat_id, chat.title or "", owner_id, photo_url),
    )
    await db.commit()

async def close_db() -> None:
    if db:
        await db.close()

# ---------- Utilities ----------

LINK_REGEX = re.compile(r"(https?://|t\.me/|telegram\.me/)", re.IGNORECASE)

def parse_duration(value: str) -> int:
    unit = value[-1]
    number = int(value[:-1])
    return number * {"s": 1, "m": 60, "h": 3600}.get(unit, 1)

async def is_admin(client: Client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    except Exception:
        return False

async def delete_later(client: Client, chat_id: int, message_id: int, delay: int) -> None:
    await asyncio.sleep(delay)
    with suppress(Exception):
        await client.delete_messages(chat_id, message_id)

# ---------- UI Panels ----------

async def build_group_panel(chat_id: int) -> InlineKeyboardMarkup:
    editmode = await get_setting(chat_id, "editmode", "0") == "1"
    autodel = await get_setting(chat_id, "autodelete", "0") == "1"
    linkfilter = await get_setting(chat_id, "linkfilter", "0") == "1"
    biolink = await get_setting(chat_id, "biolink", "0") == "1"
    buttons = [
        [
            InlineKeyboardButton(f"Link Filter {'✅' if linkfilter else '❌'}", f"toggle|{chat_id}|linkfilter"),
            InlineKeyboardButton(f"Bio Link {'✅' if biolink else '❌'}", f"toggle|{chat_id}|biolink"),
        ],
        [
            InlineKeyboardButton(f"Auto Delete {'✅' if autodel else '❌'}", f"toggle|{chat_id}|autodelete"),
            InlineKeyboardButton(f"Edit Mode {'✅' if editmode else '❌'}", f"toggle|{chat_id}|editmode"),
        ],
        [InlineKeyboardButton("📡 Ping", f"ping|{chat_id}"), InlineKeyboardButton("❌ Close", "close")],
    ]
    return InlineKeyboardMarkup(buttons)

def build_private_panel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛠️ My Settings", "noop"), InlineKeyboardButton("📖 Help", "noop")],
        [InlineKeyboardButton("❌ Close", "close")],
    ])

# ---------- Pyrogram Client ----------

app = Client(
    "oxeignbot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    parse_mode=ParseMode.HTML,
)

# ---------- Commands ----------

@app.on_message(filters.command(["start", "menu", "help", "settings"]))
async def start_handler(client: Client, message: Message):
    if message.chat.type in ("group", "supergroup"):
        await store_group_meta(message.chat.id, client)
        panel = await build_group_panel(message.chat.id)
    else:
        panel = build_private_panel()
    await message.reply_text("🛡️ OxeignBot Control Panel", reply_markup=panel)

@app.on_message(filters.command("ping"))
async def ping_cmd(client: Client, message: Message):
    start = asyncio.get_event_loop().time()
    msg = await message.reply_text("📡 Pong...")
    end = asyncio.get_event_loop().time()
    await msg.edit_text(f"🎉 Pong: <b>{int((end - start) * 1000)}ms</b>")

@app.on_message(filters.command(["editmode", "linkfilter", "biolink"]))
async def toggle_feature(client: Client, message: Message):
    cmd = message.command[0].lstrip("/")
    if message.chat.type not in ("group", "supergroup"):
        return await message.reply_text("🔒 Group-only command.")
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text("🚫 Admins only.")
    val = await toggle_setting(message.chat.id, cmd)
    await message.reply_text(f"{cmd.capitalize()} {'enabled ✅' if val == '1' else 'disabled ❌'}")

@app.on_message(filters.command("autodelete"))
async def cmd_autodelete(client: Client, message: Message):
    if message.chat.type != ChatType.SUPERGROUP:
        return await message.reply_text("Group only.")
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) == 1:
        enabled = await get_setting(message.chat.id, "autodelete", "0")
        interval = await get_setting(message.chat.id, "autodelete_interval", "0")
        return await message.reply_text(
            f"Auto delete is {'on' if enabled == '1' else 'off'} ({interval}s)")
    try:
        seconds = parse_duration(parts[1])
        await set_setting(message.chat.id, "autodelete", "1")
        await set_setting(message.chat.id, "autodelete_interval", str(seconds))
        await message.reply_text(f"Auto delete set to {seconds} seconds")
    except Exception:
        await message.reply_text("❌ Invalid duration. Use 30s, 2m, 1h, etc.")

# ---------- Admin Actions ----------

async def admin_action(client: Client, message: Message, action: str):
    if message.chat.type not in ("group", "supergroup"):
        return await message.reply_text("Group only command")
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text("Admins only")
    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await message.reply_text("Reply to a user's message.")

    user = message.reply_to_message.from_user
    try:
        if action == "ban":
            await client.ban_chat_member(message.chat.id, user.id)
        elif action == "kick":
            await client.ban_chat_member(message.chat.id, user.id)
            await client.unban_chat_member(message.chat.id, user.id)
        elif action == "mute":
            await client.restrict_chat_member(message.chat.id, user.id, ChatPermissions())
        await message.reply_text(f"{action.title()} successful ✅")
    except Exception as e:
        await message.reply_text(f"❌ Failed: {e}")

@app.on_message(filters.command("ban"))   async def ban(client, m): await admin_action(client, m, "ban")
@app.on_message(filters.command("kick"))  async def kick(client, m): await admin_action(client, m, "kick")
@app.on_message(filters.command("mute"))  async def mute(client, m): await admin_action(client, m, "mute")

# ---------- Auto-filters ----------

@app.on_message(filters.group & ~filters.service)
async def filter_links(client: Client, message: Message):
    text = message.text or message.caption or ""
    chat_id = message.chat.id

    if await get_setting(chat_id, "linkfilter", "0") == "1" and LINK_REGEX.search(text):
        with suppress(Exception): await message.delete(); return

    if await get_setting(chat_id, "biolink", "0") == "1" and message.from_user:
        try:
            user = await client.get_users(message.from_user.id)
            if user.bio and LINK_REGEX.search(user.bio):
                with suppress(Exception): await message.delete(); return
        except: pass

    if await get_setting(chat_id, "autodelete", "0") == "1":
        delay = int(await get_setting(chat_id, "autodelete_interval", "30"))
        asyncio.create_task(delete_later(client, chat_id, message.id, delay))

@app.on_edited_message(filters.group & ~filters.service)
async def on_edit(client: Client, message: Message):
    if await get_setting(message.chat.id, "editmode", "0") == "1":
        asyncio.create_task(delete_later(client, message.chat.id, message.id, 900))

# ---------- Callbacks ----------

@app.on_callback_query()
async def callback_handler(client: Client, query: CallbackQuery):
    if query.data == "close":
        with suppress(Exception): await query.message.delete()
        return
    elif query.data.startswith("ping"):
        await query.answer("📡 Pong")
        return
    elif query.data.startswith("toggle"):
        _, chat_id, key = query.data.split("|")
        if not await is_admin(client, int(chat_id), query.from_user.id):
            return await query.answer("Admins only", show_alert=True)
        value = await toggle_setting(int(chat_id), key)
        panel = await build_group_panel(int(chat_id))
        with suppress(Exception):
            await query.message.edit_reply_markup(panel)
        await query.answer("Toggled successfully ✅")
    else:
        await query.answer("⚙️ Not implemented", show_alert=False)

# ---------- Entrypoint ----------

async def main():
    await init_db(DB_PATH)
    async with app:
        logger.info("✅ OxeignBot is running")
        await idle()
    await close_db()

if __name__ == "__main__":
    asyncio.run(main())
