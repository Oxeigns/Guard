from pyrogram import filters, Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message
from utils.storage import is_approved, get_warnings, increment_warning, reset_warning
from utils.perms import is_admin
from config import LOG_CHANNEL_ID

LINK_KEYWORDS = ["http", "https", "t.me", ".me", ".com", ".link"]

def register(app: Client):
    @app.on_message(filters.group & filters.text)
    async def bio_filter(client, message: Message):
        user = message.from_user
        if not user or not user.bio:
            return

        if await is_admin(client, message, user.id) or user.is_bot:
            return

        if not await is_approved(message.chat.id, user.id):
            if any(keyword in user.bio.lower() for keyword in LINK_KEYWORDS):
                await message.delete()
                warning_count = await increment_warning(message.chat.id, user.id)

                if warning_count == 1:
                    warning = "⚠️ Warning 1"
                elif warning_count == 2:
                    warning = "⚠️ Warning 2"
                elif warning_count >= 3:
                    warning = "⛔ Final Warning\n🔇 User muted permanently."
                    await client.restrict_chat_member(
                        message.chat.id,
                        user.id,
                        permissions={}
                    )
                    await log_action(client, f"🧹 **User muted permanently**\n👤 [{user.first_name}](tg://user?id={user.id})\n🆔 `{user.id}`\n📛 Warnings exceeded", message.chat.id)
                    await reset_warning(message.chat.id, user.id)
                else:
                    return

                await message.reply_text(warning, quote=True)

async def log_action(client, text, chat_id):
    from datetime import datetime
    await client.send_message(
        LOG_CHANNEL_ID,
        f"**🔒 Moderation Log**\n{text}\n🕒 `{datetime.utcnow().isoformat()}`",
        parse_mode="Markdown"
    )
