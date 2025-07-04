import logging
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from utils.perms import is_admin
from utils.errors import catch_errors
from utils.db import toggle_setting, get_setting, set_setting

logger = logging.getLogger(__name__)
DEFAULT_AUTODELETE_SECONDS = 60


def register(app: Client) -> None:
    @app.on_message(filters.command("biolink") & filters.group)
    @catch_errors
    async def cmd_biolink(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text("🔒 <b>Admins only.</b>", parse_mode=ParseMode.HTML)
            return
        state = await toggle_setting(message.chat.id, "biolink")
        await message.reply_text(
            f"🔗 Bio filter {'enabled ✅' if state == '1' else 'disabled ❌'}",
            parse_mode=ParseMode.HTML,
        )

    @app.on_message(filters.command("editmode") & filters.group)
    @catch_errors
    async def cmd_editmode(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text("🔒 <b>Admins only.</b>", parse_mode=ParseMode.HTML)
            return
        state = await toggle_setting(message.chat.id, "editmode")
        await message.reply_text(
            f"✏️ Edit mode {'enabled ✅' if state == '1' else 'disabled ❌'}",
            parse_mode=ParseMode.HTML,
        )

    @app.on_message(filters.command(["autodelete", "setautodelete"]) & filters.group)
    @catch_errors
    async def cmd_autodelete(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text("🔒 <b>Admins only.</b>", parse_mode=ParseMode.HTML)
            return
        if len(message.command) == 1:
            current = await get_setting(message.chat.id, "autodelete", "0")
            interval = await get_setting(message.chat.id, "autodelete_interval", "0")
            await message.reply_text(
                f"🕒 Auto-delete: <code>{interval}s</code> ({'on' if current=='1' else 'off'})",
                parse_mode=ParseMode.HTML,
            )
            return
        try:
            seconds = int(message.command[1])
            if seconds <= 0:
                raise ValueError
        except ValueError:
            await message.reply_text("⚠️ Usage: /autodelete <seconds>", parse_mode=ParseMode.HTML)
            return
        await set_setting(message.chat.id, "autodelete", "1")
        await set_setting(message.chat.id, "autodelete_interval", str(seconds))
        await message.reply_text(
            f"🧹 Auto-delete set to <b>{seconds}</b> seconds",
            parse_mode=ParseMode.HTML,
        )

    @app.on_message(filters.command("autodeleteon") & filters.group)
    @catch_errors
    async def enable_autodel(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text("🔒 <b>Admins only.</b>", parse_mode=ParseMode.HTML)
            return
        await set_setting(message.chat.id, "autodelete", "1")
        await set_setting(message.chat.id, "autodelete_interval", str(DEFAULT_AUTODELETE_SECONDS))
        await message.reply_text(
            f"✅ Auto-delete enabled: <code>{DEFAULT_AUTODELETE_SECONDS}s</code>",
            parse_mode=ParseMode.HTML,
        )

    @app.on_message(filters.command("autodeleteoff") & filters.group)
    @catch_errors
    async def disable_autodel(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text("🔒 <b>Admins only.</b>", parse_mode=ParseMode.HTML)
            return
        await set_setting(message.chat.id, "autodelete", "0")
        await set_setting(message.chat.id, "autodelete_interval", "0")
        await message.reply_text("🧹 Auto-delete disabled.", parse_mode=ParseMode.HTML)

    @app.on_message(filters.command("linkfilter") & filters.group)
    @catch_errors
    async def cmd_linkfilter(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text("🔒 <b>Admins only.</b>", parse_mode=ParseMode.HTML)
            return
        arg = message.command[1].lower() if len(message.command) > 1 else None
        if arg in {"on", "off"}:
            state = "1" if arg == "on" else "0"
            await set_setting(message.chat.id, "linkfilter", state)
        else:
            state = await toggle_setting(message.chat.id, "linkfilter")
        await message.reply_text(
            f"🔗 Link filter {'enabled ✅' if state == '1' else 'disabled ❌'}",
            parse_mode=ParseMode.HTML,
        )

    @app.on_message(filters.command("autodeleteedited") & filters.group)
    @catch_errors
    async def cmd_autodeleteedited(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text("🔒 <b>Admins only.</b>", parse_mode=ParseMode.HTML)
            return
        arg = message.command[1].lower() if len(message.command) > 1 else None
        if arg in {"on", "off"}:
            state = "1" if arg == "on" else "0"
            await set_setting(message.chat.id, "editmode", state)
        else:
            state = await toggle_setting(message.chat.id, "editmode")
        await message.reply_text(
            f"📝 Edited delete {'enabled ✅' if state == '1' else 'disabled ❌'}",
            parse_mode=ParseMode.HTML,
        )
