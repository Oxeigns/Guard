import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode, ChatType
from utils.errors import catch_errors
from handlers.panels import send_start  # ✅ Correct import from your module

logger = logging.getLogger(__name__)


def register(app: Client) -> None:
    print("✅ Registered: general.py")

    # Main panel route
    @app.on_message(filters.command(["start", "help", "menu", "panel"]) & (filters.private | filters.group))
    @catch_errors
    async def send_panel(client: Client, message: Message):
        logger.info("[GENERAL] panel command in chat %s", message.chat.id)
        await send_start(client, message)

    # ID Command
    @app.on_message(filters.command("id") & (filters.private | filters.group))
    @catch_errors
    async def id_cmd(client: Client, message: Message) -> None:
        logger.info("[GENERAL] id command in chat %s", message.chat.id)

        target = (
            message.reply_to_message.from_user
            if message.reply_to_message and message.reply_to_message.from_user
            else message.from_user or message.sender_chat
        )

        if message.chat.type in {ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL}:
            text = f"<b>Chat ID:</b> <code>{message.chat.id}</code>"
            if target:
                text += f"\n<b>User ID:</b> <code>{target.id}</code>"
        else:
            text = f"<b>Your ID:</b> <code>{target.id}</code>"

        await message.reply_text(text, parse_mode=ParseMode.HTML)

    # Ping Command
    @app.on_message(filters.command("ping") & (filters.private | filters.group))
    @catch_errors
    async def ping_cmd(client: Client, message: Message) -> None:
        logger.info("[GENERAL] ping command in chat %s", message.chat.id)
        await message.reply_text("🏓 Pong!")

    # DM fallback
    @app.on_message(filters.private & ~filters.command("") & ~filters.via_bot)
    @catch_errors
    async def dm_fallback(client: Client, message: Message) -> None:
        logger.info("[DM FALLBACK] %s: %s", message.from_user.id, message.text)
        await message.reply_text("🤖 I received your message, but didn’t understand it.")

    # Group fallback
    @app.on_message(filters.group & ~filters.command("") & ~filters.service)
    @catch_errors
    async def group_fallback(client: Client, message: Message) -> None:
        logger.info("[GROUP FALLBACK] %s/%s: %s", message.chat.id, message.from_user.id, message.text)
