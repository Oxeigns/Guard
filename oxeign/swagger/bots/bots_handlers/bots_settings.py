from pyrogram import Client, filters
from pyrogram.types import Message, ChatMemberUpdated
from .panels import send_start  # ✅ Only need send_start now


def register(app: Client):
    @app.on_message(filters.command(["start", "help", "menu"]))
    async def handle_main_commands(client: Client, message: Message):
        # ✅ Always show the welcome photo panel, in both DM and group
        await send_start(client, message)

    @app.on_chat_member_updated()
    async def on_bot_added(client: Client, update: ChatMemberUpdated):
        if update.new_chat_member.user.is_self:
            try:
                await send_start(client, update)
            except Exception as e:
                print(f"[BOT JOIN ERROR] {e}")
