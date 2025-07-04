import logging
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import ParseMode

from utils.perms import is_admin
from utils.errors import catch_errors
from utils.db import (
    approve_user,
    unapprove_user,
    get_approved,
    is_approved,
    toggle_approval_mode,
    set_approval_mode,
    get_approval_mode,
    set_setting,
)

logger = logging.getLogger(__name__)


def register(app: Client) -> None:
    async def admin_action(message: Message, action: str) -> None:
        """Perform ban/kick/mute actions if admin and valid reply."""
        if message.chat.type not in {"group", "supergroup"}:
            await message.reply_text("❗ Group-only command.", parse_mode=ParseMode.HTML)
            return
        if not await is_admin(app, message):
            await message.reply_text("🔒 <b>Admins only.</b>", parse_mode=ParseMode.HTML)
            return
        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.reply_text("📌 Reply to a user's message.", parse_mode=ParseMode.HTML)
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
        except Exception as e:
            logger.error(f"{action} failed: {e}")
            await message.reply_text(f"❌ Failed: {e}")

    async def require_admin_reply(message: Message, action: str):
        """Ensure command is by admin and used as a reply."""
        if not await is_admin(app, message):
            await message.reply_text("🚫 <b>Only admins can do this.</b>", parse_mode=ParseMode.HTML)
            return None
        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.reply_text(f"📌 <b>Reply to a user's message to {action}.</b>", parse_mode=ParseMode.HTML)
            return None
        user = message.reply_to_message.from_user
        return user.id, f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

    @app.on_message(filters.command("ban") & filters.group)
    @catch_errors
    async def cmd_ban(client: Client, message: Message):
        await admin_action(message, "ban")

    @app.on_message(filters.command("kick") & filters.group)
    @catch_errors
    async def cmd_kick(client: Client, message: Message):
        await admin_action(message, "kick")

    @app.on_message(filters.command("mute") & filters.group)
    @catch_errors
    async def cmd_mute(client: Client, message: Message):
        await admin_action(message, "mute")

    @app.on_message(filters.command("approve") & filters.group)
    @catch_errors
    async def approve_cmd(client: Client, message: Message):
        result = await require_admin_reply(message, "approve")
        if result:
            user_id, mention = result
            await approve_user(message.chat.id, user_id)
            await message.reply_text(f"✅ <b>Approved</b> {mention}", parse_mode=ParseMode.HTML)

    @app.on_message(filters.command("unapprove") & filters.group)
    @catch_errors
    async def unapprove_cmd(client: Client, message: Message):
        result = await require_admin_reply(message, "unapprove")
        if result:
            user_id, mention = result
            await unapprove_user(message.chat.id, user_id)
            await message.reply_text(f"❌ <b>Unapproved</b> {mention}", parse_mode=ParseMode.HTML)

    @app.on_message(filters.command("viewapproved") & filters.group)
    @catch_errors
    async def view_approved(client: Client, message: Message):
        if not await is_admin(app, message):
            await message.reply_text("🚫 <b>Only admins can view approvals.</b>", parse_mode=ParseMode.HTML)
            return
        users = await get_approved(message.chat.id)
        if not users:
            await message.reply_text("📭 <i>No approved users found.</i>", parse_mode=ParseMode.HTML)
        else:
            text = "<b>📋 Approved Users:</b>\n" + "\n".join(f"• <code>{u}</code>" for u in users)
            await message.reply_text(text, parse_mode=ParseMode.HTML)

    @app.on_message(filters.command("approval") & filters.group)
    @catch_errors
    async def approval_mode_cmd(client: Client, message: Message):
        if not await is_admin(app, message):
            await message.reply_text("🔒 <b>Only admins can change approval mode.</b>", parse_mode=ParseMode.HTML)
            return

        if len(message.command) == 1:
            enabled = await toggle_approval_mode(message.chat.id)
        else:
            mode = message.command[1].lower()
            if mode in {"on", "enable", "true"}:
                await set_approval_mode(message.chat.id, True)
                enabled = True
            elif mode in {"off", "disable", "false"}:
                await set_approval_mode(message.chat.id, False)
                enabled = False
            else:
                await message.reply_text("❗ <b>Usage:</b> <code>/approval [on|off]</code>", parse_mode=ParseMode.HTML)
                return

        await message.reply_text(
            f"🔄 <b>Approval mode is now {'ENABLED ✅' if enabled else 'DISABLED ❌'}</b>",
            parse_mode=ParseMode.HTML,
        )

    def _parse_toggle_arg(arg: str | None) -> str | None:
        """Return '1' or '0' for on/off args, or None if invalid."""
        if not arg:
            return None
        arg = arg.lower()
        if arg in {"on", "enable", "yes", "true"}:
            return "1"
        if arg in {"off", "disable", "no", "false"}:
            return "0"
        return None

    async def _require_admin(message: Message) -> bool:
        if not await is_admin(app, message):
            await message.reply_text("🔒 <b>Admins only.</b>", parse_mode=ParseMode.HTML)
            return False
        return True

    @app.on_message(filters.command("biolink") & filters.group)
    @catch_errors
    async def biolink_cmd(client: Client, message: Message):
        if not await _require_admin(message):
            return
        state = _parse_toggle_arg(message.command[1] if len(message.command) > 1 else None)
        if state is None:
            await message.reply_text("❗ <b>Usage:</b> <code>/biolink on|off</code>", parse_mode=ParseMode.HTML)
            return
        await set_setting(message.chat.id, "biolink", state)
        await message.reply_text(
            f"🌐 <b>Bio link filter {'ENABLED ✅' if state == '1' else 'DISABLED ❌'}</b>",
            parse_mode=ParseMode.HTML,
        )

    @app.on_message(filters.command("linkfilter") & filters.group)
    @catch_errors
    async def linkfilter_cmd(client: Client, message: Message):
        if not await _require_admin(message):
            return
        state = _parse_toggle_arg(message.command[1] if len(message.command) > 1 else None)
        if state is None:
            await message.reply_text(
                "❗ <b>Usage:</b> <code>/linkfilter on|off</code>",
                parse_mode=ParseMode.HTML,
            )
            return
        await set_setting(message.chat.id, "linkfilter", state)
        await message.reply_text(
            f"🔗 <b>Link filter {'ENABLED ✅' if state == '1' else 'DISABLED ❌'}</b>",
            parse_mode=ParseMode.HTML,
        )

    @app.on_message(filters.command("editmode") & filters.group)
    @catch_errors
    async def editmode_cmd(client: Client, message: Message):
        if not await _require_admin(message):
            return
        state = _parse_toggle_arg(message.command[1] if len(message.command) > 1 else None)
        if state is None:
            await message.reply_text(
                "❗ <b>Usage:</b> <code>/editmode on|off</code>",
                parse_mode=ParseMode.HTML,
            )
            return
        await set_setting(message.chat.id, "editmode", state)
        await message.reply_text(
            f"✏️ <b>Edit mode {'ENABLED ✅' if state == '1' else 'DISABLED ❌'}</b>",
            parse_mode=ParseMode.HTML,
        )

    @app.on_message(filters.command("autodeleteoff") & filters.group)
    @catch_errors
    async def autodelete_off_cmd(client: Client, message: Message):
        if not await _require_admin(message):
            return
        await set_setting(message.chat.id, "autodelete", "0")
        await set_setting(message.chat.id, "autodelete_interval", "0")
        await message.reply_text("🧹 <b>Auto delete disabled.</b>", parse_mode=ParseMode.HTML)

    @app.on_message(filters.command("autodelete") & filters.group)
    @catch_errors
    async def autodelete_cmd(client: Client, message: Message):
        if not await _require_admin(message):
            return
        if len(message.command) < 2:
            await message.reply_text(
                "❗ <b>Usage:</b> <code>/autodelete &lt;seconds&gt;</code>",
                parse_mode=ParseMode.HTML,
            )
            return
        try:
            seconds = int(message.command[1])
            if seconds <= 0:
                raise ValueError
        except ValueError:
            await message.reply_text("❗ Provide a valid number of seconds.", parse_mode=ParseMode.HTML)
            return

        await set_setting(message.chat.id, "autodelete", "1")
        await set_setting(message.chat.id, "autodelete_interval", str(seconds))
        await message.reply_text(
            f"🧹 <b>Auto delete enabled for {seconds}s.</b>",
            parse_mode=ParseMode.HTML,
        )
