import asyncio
import logging
from urllib import request, parse, error

logger = logging.getLogger(__name__)


async def set_webhook(bot_token: str, url: str) -> None:
    """
    Set the Telegram bot webhook using the Telegram Bot API.
    
    Args:
        bot_token (str): Your bot's token from BotFather.
        url (str): The public HTTPS URL where Telegram will send updates.
    """
    api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    data = parse.urlencode({"url": url}).encode("utf-8")
    req = request.Request(api_url, data=data)

    loop = asyncio.get_running_loop()

    try:
        logger.debug(f"Setting webhook to: {url}")
        resp = await loop.run_in_executor(None, request.urlopen, req)
        response_data = resp.read()
        logger.info("✅ Webhook successfully set via Bot API.")
    except error.URLError as exc:
        logger.error("❌ Failed to set webhook: %s", exc.reason)
    except Exception as exc:
        logger.exception("🔥 Unexpected error while setting webhook: %s", exc)
