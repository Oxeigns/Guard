"""Expose all handler modules and provide a helper to register them."""

from importlib import import_module
from pyrogram import Client

__all__ = [
    "biofilter",
    "autodelete",
    "approval",
    "panel",
    "logs",
    "commands",
]

MODULES = __all__

# Pre-import modules so they are available when ``from handlers import ...`` is used
from . import (  # noqa: E402
    biofilter as _biofilter,  # noqa: F401
    autodelete as _autodelete,  # noqa: F401
    approval as _approval,  # noqa: F401
    panel as _panel,  # noqa: F401
    logs as _logs,  # noqa: F401
    commands as _commands,  # noqa: F401
)


def register_all(app: Client) -> None:
    """Register all handlers on the provided ``Client`` instance."""
    for name in MODULES:
        module = import_module(f".{name}", __name__)
        register = getattr(module, "register", None)
        if callable(register):
            register(app)
