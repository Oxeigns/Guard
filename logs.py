from datetime import datetime
from pyrogram import Client
from pyrogram.types import Chat, User
from config import LOG_CHANNEL_ID

def register(app: Client):
    pass  # No persistent handlers, only utils

async def log_event(action: str, source: Chat | User):
    if isinstance(source, Chat):
        title = source.title or "Private"
        ident = f"🆔 `{source.id}`\n🏷 Name: {title}"
    else:
        ident = f"👤 [{source.first_name}](tg://user?id={source.id})\n🆔 `{source.id}`"

    log_text = f"""**📘 Bot Log**
🔹 Action: {action}
{ident}
🕒 `{datetime.utcnow().isoformat()}`"""

    from main import app
    await app.send_message(LOG_CHANNEL_ID, log_text, parse_mode="Markdown")
