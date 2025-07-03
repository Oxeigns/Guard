import asyncio
import logging
import os
import threading
import http.server
from typing import Iterable

from pyrogram import Client, filters, idle
from pyrogram.enums import ParseMode

from config import config
import handlers.logs


class HealthHandler(logging.Handler):
    """Handler that writes logs to a file and stdout."""

    def emit(self, record: logging.LogRecord) -> None:
        print(self.format(record))


def start_health_server() -> None:
    """Expose a basic HTTP server for environments that require a port."""

    class _Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # type: ignore[override]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

    port = int(os.getenv("PORT", "8080"))
    server = http.server.HTTPServer(("0.0.0.0", port), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logging.info("Health server running on port %s", port)


async def main() -> None:
    """Start the Telegram bot."""
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), "INFO"),
        filename=config.log_file,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    start_health_server()
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
        """Send commands to the log channel and upload the log file."""
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
        try:
            await app.send_document(
                config.log_channel_id, config.log_file, caption="Self test logs"
            )
            logging.info("Self test logs uploaded")
        except Exception as exc:
            logging.exception("Failed to upload log file: %s", exc)

    await app.start()
    if config.run_self_tests:
        await run_self_tests(["/panel", "/approved", "/biomode", "/setautodelete off"])
    await idle()
    await app.stop()


if __name__ == "__main__":
    asyncio.run(main())

