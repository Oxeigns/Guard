import asyncio
import logging
from typing import Iterable

from pyrogram import Client, filters, idle
from pyrogram.enums import ParseMode

from config import config
import handlers.logs


async def main() -> None:
    """Start the Telegram bot."""
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), "INFO"),
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(config.log_file),
            logging.StreamHandler(),
        ],
    )
    app = Client(
        "guard_bot",
        api_id=config.api_id,
        api_hash=config.api_hash,
        bot_token=config.bot_token,
        plugins={"root": "handlers"},
    )

    @app.on_message(filters.private & filters.command("start"))
    async def start_handler(_, msg):
        if config.start_image:
            await msg.reply_photo(
                config.start_image,
                caption="Welcome!",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await msg.reply_text("Welcome!", parse_mode=ParseMode.MARKDOWN)
        await handlers.logs.start_log(app, msg)

    @app.on_message(filters.new_chat_members)
    async def join_handler(_, msg):
        if msg.new_chat_members and any(u.is_self for u in msg.new_chat_members):
            await handlers.logs.added_to_group(app, msg)

    @app.on_message(filters.left_chat_member)
    async def left_handler(_, msg):
        if msg.left_chat_member and msg.left_chat_member.is_self:
            await handlers.logs.removed_from_group(app, msg.chat)

    async def run_self_tests(commands: Iterable[str]) -> None:
        """Run a series of bot commands for diagnostics."""
        if not config.log_channel_id:
            logging.info("No LOG_CHANNEL_ID set; skipping self tests")
            return
        for cmd in commands:
            try:
                await app.send_message(config.log_channel_id, cmd)
                logging.info("Self test command sent: %s", cmd)
                await asyncio.sleep(1)
            except Exception as exc:
                logging.exception("Failed to send %s: %s", cmd, exc)

    async def start_http_server(port: int):
        """Run a minimal HTTP server for health checks."""
        async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
            try:
                await reader.read(1024)
                writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nok")
                await writer.drain()
            finally:
                writer.close()
        server = await asyncio.start_server(handle, "0.0.0.0", port)
        logging.info("Health server running on port %s", port)
        return server

    await app.start()
    server = None
    if config.port:
        try:
            server = await start_http_server(config.port)
        except Exception as exc:
            logging.exception("Failed to start health server: %s", exc)
    if config.run_self_tests:
        await run_self_tests(["/panel", "/approved", "/biomode", "/setautodelete off"])
    await idle()
    await app.stop()
    if server:
        server.close()
        await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())

