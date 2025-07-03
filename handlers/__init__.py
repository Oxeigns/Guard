"""Expose all handler modules and provide a helper to register them."""

import logging
from importlib import import_module
from pathlib import Path
from pyrogram import Client

logger = logging.getLogger(__name__)

MODULES = [
    p.stem
    for p in Path(__file__).parent.glob("*.py")
    if p.stem not in {"__init__", "logs"}
]

__all__ = MODULES


def init_all(app: Client) -> None:
    """Register all handlers on the provided ``Client`` instance."""
    for name in MODULES:
        module = import_module(f".{name}", __name__)
        register = getattr(module, "register", None)
        if callable(register):
            logger.info("Registering handlers from %s", name)
            register(app)
