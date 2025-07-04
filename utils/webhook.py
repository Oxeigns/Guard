import asyncio
import logging
from urllib import request, parse, error

logger = logging.getLogger(__name__)

async def set_webhook(bot_token: str, url: str) -> None:
    """Set the Telegram bot webhook via the Bot API."""
    api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    data = parse.urlencode({"url": url}).encode()
    req = request.Request(api_url, data=data)
    loop = asyncio.get_running_loop()
    try:
        resp = await loop.run_in_executor(None, request.urlopen, req)
        resp.read()  # Consume response
        logger.info("Webhook configured via Bot API")
    except error.URLError as exc:
        logger.error("Failed to set webhook: %s", exc)
