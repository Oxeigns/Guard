"""Utility functions for error handling used across the bot."""

from __future__ import annotations

import functools
import logging

logger = logging.getLogger(__name__)


def catch_errors(func):
    """Decorator that logs exceptions raised by async handlers."""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception:  # noqa: BLE001
            logger.exception("Unhandled exception in %s", func.__name__)

    return wrapper


__all__ = ["catch_errors"]
