from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.handlers import MessageHandler
from pyrogram.enums import ParseMode
from oxeign.utils.filters import admin_filter
from oxeign.swagger.blacklist import add_word, remove_word, list_words
from oxeign.utils.logger import log_to_channel


async def blacklist_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        words = await list_words(message.chat.id)
        text = "\n".join(words) or "No words set"
        return await message.reply(f"<b>Blacklisted Words</b>\n{text}", parse_mode=ParseMode.HTML)
    action = message.command[1].lower()
    if action == "add" and len(message.command) > 2:
        word = message.command[2].lower()
        await add_word(message.chat.id, word)
        await message.reply("✅ <b>Word added</b>", parse_mode=ParseMode.HTML)
        await log_to_channel(client, f"Added blacklist word '{word}' in {message.chat.id}")
    elif action in {"remove", "del"} and len(message.command) > 2:
        word = message.command[2].lower()
        await remove_word(message.chat.id, word)
        await message.reply("✅ <b>Word removed</b>", parse_mode=ParseMode.HTML)
        await log_to_channel(client, f"Removed blacklist word '{word}' in {message.chat.id}")
    elif action == "list":
        words = await list_words(message.chat.id)
        text = "\n".join(words) or "No words set"
        await message.reply(f"<b>Blacklisted Words</b>\n{text}", parse_mode=ParseMode.HTML)
    else:
        await message.reply("❌ <b>Usage:</b> /blacklist [add|remove|list] <word>", parse_mode=ParseMode.HTML)


async def enforce_blacklist(client: Client, message: Message):
    if not message.text or message.service or not message.from_user:
        return
    words = await list_words(message.chat.id)
    if not words:
        return
    lower = message.text.lower()
    for word in words:
        if word in lower:
            await message.delete()
            await log_to_channel(client, f"Deleted blacklisted word in {message.chat.id} from {message.from_user.id}")
            break


def register(app: Client):
    app.add_handler(MessageHandler(blacklist_cmd, filters.command("blacklist") & admin_filter))
    app.add_handler(MessageHandler(enforce_blacklist, filters.group & ~filters.service))
