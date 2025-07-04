import functools
import logging

logger = logging.getLogger(__name__)


def catch_errors(func):
    """Decorator to log exceptions from async handlers without crashing."""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception:  # noqa: BLE001
            logger.exception("Unhandled exception in %s", func.__name__)
    return wrapper
