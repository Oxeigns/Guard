from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, ChatMemberUpdated
from .bots_settings import send_start, send_control_panel


def register(app: Client):
    @app.on_message(filters.command(["start", "help", "menu"]))
    async def handle_main_commands(client: Client, message: Message):
        if message.chat.type == "private":
            await send_start(client, message)
        else:
            await send_control_panel(client, message)

    @app.on_chat_member_updated()
    async def on_bot_added(client: Client, update: ChatMemberUpdated):
        if update.new_chat_member.user.is_self:
            try:
                await send_control_panel(client, update.chat)
            except Exception as e:
                print(f"[BOT JOIN ERROR] {e}")
