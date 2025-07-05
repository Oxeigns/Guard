import logging
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import ParseMode
from utils.db import (
    approve_user,
    unapprove_user,
    get_approved,
    increment_warning,
    reset_warning,
    set_setting,
    set_bio_filter,
)

logger = logging.getLogger(__name__)


async def _require_admin_group(client: Client, message: Message) -> bool:
    if message.chat.type not in {"group", "supergroup"}:
        await message.reply_text("❗ Group-only command")
        return False
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in ("administrator", "creator"):
        await message.reply_text("🔒 Admins only")
        return False
    return True


def register(app: Client) -> None:
    async def _admin_action(message: Message, action: str) -> None:
        if not await _require_admin_group(app, message):
            return
        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.reply_text("📌 Reply to a user")
            return
        user = message.reply_to_message.from_user
        try:
            if action == "ban":
                await app.ban_chat_member(message.chat.id, user.id)
            elif action == "kick":
                await app.ban_chat_member(message.chat.id, user.id)
                await app.unban_chat_member(message.chat.id, user.id)
            elif action == "mute":
                await app.restrict_chat_member(message.chat.id, user.id, ChatPermissions())
            await message.reply_text(f"{action.title()} successful ✅")
        except Exception as exc:  # noqa: BLE001
            logger.error("%s failed: %s", action, exc)
            await message.reply_text(f"❌ Failed: {exc}")

    @app.on_message(filters.command("ban"))
    async def ban_cmd(_, message: Message):
        await _admin_action(message, "ban")

    @app.on_message(filters.command("kick"))
    async def kick_cmd(_, message: Message):
        await _admin_action(message, "kick")

    @app.on_message(filters.command("mute"))
    async def mute_cmd(_, message: Message):
        await _admin_action(message, "mute")

    @app.on_message(filters.command("warn"))
    async def warn_cmd(_, message: Message):
        if not await _require_admin_group(app, message):
            return
        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.reply_text("📌 Reply to a user")
            return
        user = message.reply_to_message.from_user
        count = await increment_warning(message.chat.id, user.id)
        if count >= 3:
            await app.restrict_chat_member(message.chat.id, user.id, ChatPermissions())
            await reset_warning(message.chat.id, user.id)
            await message.reply_text(f"🔇 {user.mention} muted (3 warnings)")
        else:
            await message.reply_text(f"⚠ Warned {user.mention}. ({count}/3)")

    @app.on_message(filters.command("resetwarn"))
    async def resetwarn_cmd(_, message: Message):
        if not await _require_admin_group(app, message):
            return
        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.reply_text("📌 Reply to a user")
            return
        user = message.reply_to_message.from_user
        await reset_warning(message.chat.id, user.id)
        await message.reply_text(f"🧹 Warnings reset for {user.mention}")

    async def _toggle_setting(message: Message, key: str, value: str, label: str):
        if not await _require_admin_group(app, message):
            return
        await set_setting(message.chat.id, key, value)
        state = "ENABLED ✅" if value == "1" else "DISABLED ❌"
        await message.reply_text(f"{label} {state}")

    @app.on_message(filters.command("biolink"))
    async def biolink_cmd(_, message: Message):
        if len(message.command) < 2:
            await message.reply_text("Usage: /biolink on|off")
            return
        state = message.command[1].lower() in {"on", "enable", "1", "true"}
        await set_bio_filter(message.chat.id, state)
        await message.reply_text(
            f"🌐 Bio link filter {'ENABLED ✅' if state else 'DISABLED ❌'}"
        )

    @app.on_message(filters.command("linkfilter"))
    async def linkfilter_cmd(_, message: Message):
        if len(message.command) < 2:
            await message.reply_text("Usage: /linkfilter on|off")
            return
        state = message.command[1].lower() in {"on", "enable", "1", "true"}
        await _toggle_setting(message, "linkfilter", "1" if state else "0", "🔗 Link filter")

    @app.on_message(filters.command("editfilter"))
    async def editfilter_cmd(_, message: Message):
        if len(message.command) < 2:
            await message.reply_text("Usage: /editfilter on|off")
            return
        state = message.command[1].lower() in {"on", "enable", "1", "true"}
        await _toggle_setting(message, "editmode", "1" if state else "0", "✏️ Edit filter")

    @app.on_message(filters.command("setautodelete"))
    async def set_autodelete_cmd(_, message: Message):
        if not await _require_admin_group(app, message):
            return
        seconds = 0
        if len(message.command) > 1:
            try:
                seconds = int(message.command[1])
                if seconds < 0:
                    raise ValueError
            except ValueError:
                await message.reply_text("❗ Provide a valid number of seconds")
                return
        await set_setting(message.chat.id, "autodelete_interval", str(seconds))
        if seconds:
            await message.reply_text(f"🧹 Auto delete set to {seconds}s")
        else:
            await message.reply_text("🧹 Auto delete disabled")

    @app.on_message(filters.command("approve"))
    async def approve_cmd(_, message: Message):
        if not await _require_admin_group(app, message):
            return
        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.reply_text("Reply to a user")
            return
        user = message.reply_to_message.from_user
        await approve_user(message.chat.id, user.id)
        await message.reply_text(f"✅ Approved {user.mention}")

    @app.on_message(filters.command("unapprove"))
    async def unapprove_cmd(_, message: Message):
        if not await _require_admin_group(app, message):
            return
        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.reply_text("Reply to a user")
            return
        user = message.reply_to_message.from_user
        await unapprove_user(message.chat.id, user.id)
        await message.reply_text(f"❌ Unapproved {user.mention}")

    @app.on_message(filters.command("approved"))
    async def approved_cmd(_, message: Message):
        if not await _require_admin_group(app, message):
            return
        users = await get_approved(message.chat.id)
        if not users:
            await message.reply_text("No approved users")
        else:
            text = "<b>Approved Users:</b>\n" + "\n".join(f"- <code>{uid}</code>" for uid in users)
            await message.reply_text(text, parse_mode=ParseMode.HTML)
