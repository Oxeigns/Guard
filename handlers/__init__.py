"""Expose all handler modules and provide a helper to register them."""

from importlib import import_module
from pyrogram import Client

MODULES = [
    "biofilter",
    "autodelete",
    "approval",
    "panel",
    "logs",
    "commands",
]

# Pre-import modules so they are available when ``from handlers import ...`` is used
from . import biofilter, autodelete, approval, panel, logs, commands

__all__ = MODULES


def register_all(app: Client) -> None:
    """Register all handlers on the provided ``Client`` instance."""
    for name in MODULES:
        module = import_module(f".{name}", __name__)
        register = getattr(module, "register", None)
        if callable(register):
            register(app)
