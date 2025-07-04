import logging
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from utils.perms import is_admin
from utils.errors import catch_errors
from utils.db import toggle_setting, get_setting, set_setting

logger = logging.getLogger(__name__)


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

    @app.on_message(filters.command("setautodelete") & filters.group)
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
        except ValueError:
            await message.reply_text("⚠️ Usage: /setautodelete <seconds>", parse_mode=ParseMode.HTML)
            return
        if seconds <= 0:
            await set_setting(message.chat.id, "autodelete", "0")
            await set_setting(message.chat.id, "autodelete_interval", "0")
            await message.reply_text("🧹 Auto-delete disabled.", parse_mode=ParseMode.HTML)
        else:
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
        interval = await get_setting(message.chat.id, "autodelete_interval", "60")
        await set_setting(message.chat.id, "autodelete_interval", interval)
        await message.reply_text(
            f"✅ Auto-delete enabled: <code>{interval}s</code>",
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

    @app.on_message(filters.command("setpunishment") & filters.group)
    @catch_errors
    async def cmd_setpunishment(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text("🔒 <b>Admins only.</b>", parse_mode=ParseMode.HTML)
            return
        if len(message.command) < 3:
            await message.reply_text(
                "Usage: /setpunishment <biolink|linkfilter> <delete|warn|ban>",
                parse_mode=ParseMode.HTML,
            )
            return
        feature = message.command[1].lower()
        mode = message.command[2].lower()
        if feature not in {"biolink", "linkfilter"} or mode not in {"delete", "warn", "ban"}:
            await message.reply_text(
                "Usage: /setpunishment <biolink|linkfilter> <delete|warn|ban>",
                parse_mode=ParseMode.HTML,
            )
            return
        await set_setting(message.chat.id, f"punish_{feature}", mode)
        await message.reply_text(
            f"Punishment for {feature} set to <b>{mode}</b>",
            parse_mode=ParseMode.HTML,
        )

    @app.on_message(filters.command("setwarnlimit") & filters.group)
    @catch_errors
    async def cmd_setwarnlimit(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text("🔒 <b>Admins only.</b>", parse_mode=ParseMode.HTML)
            return
        if len(message.command) < 2:
            await message.reply_text("Usage: /setwarnlimit <number>", parse_mode=ParseMode.HTML)
            return
        try:
            limit = int(message.command[1])
            if limit <= 0:
                raise ValueError
        except ValueError:
            await message.reply_text("Limit must be a positive number", parse_mode=ParseMode.HTML)
            return
        await set_setting(message.chat.id, "warn_limit", str(limit))
        await message.reply_text(
            f"⚠️ Warn limit set to <b>{limit}</b>",
            parse_mode=ParseMode.HTML,
        )

    @app.on_message(filters.command(["status", "settings"]) & filters.group)
    @catch_errors
    async def cmd_status(client: Client, message: Message):
        if not await is_admin(client, message):
            await message.reply_text("🔒 <b>Admins only.</b>", parse_mode=ParseMode.HTML)
            return
        auto = await get_setting(message.chat.id, "autodelete", "0") == "1"
        interval = await get_setting(message.chat.id, "autodelete_interval", "0")
        edit = await get_setting(message.chat.id, "editmode", "0") == "1"
        bio = await get_setting(message.chat.id, "biolink", "0") == "1"
        link = await get_setting(message.chat.id, "linkfilter", "0") == "1"
        bp = await get_setting(message.chat.id, "punish_biolink", "delete")
        lp = await get_setting(message.chat.id, "punish_linkfilter", "delete")
        warn = await get_setting(message.chat.id, "warn_limit", "3")
        text = (
            "<b>Current Settings:</b>\n"
            f"🗑️ Auto Delete: {'ON (' + interval + 's)' if auto else 'OFF'}\n"
            f"📝 Edit Delete: {'ON' if edit else 'OFF'}\n"
            f"🔗 Bio Link Filter: {'ON' if bio else 'OFF'} ({bp})\n"
            f"🌐 Link Filter: {'ON' if link else 'OFF'} ({lp})\n"
            f"⚠️ Warn Limit: {warn}"
        )
        await message.reply_text(text, parse_mode=ParseMode.HTML)
