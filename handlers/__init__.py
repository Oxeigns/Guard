"""Expose all handler modules and provide a helper to register them."""

from importlib import import_module
from pathlib import Path
from pyrogram import Client

MODULES = [
    p.stem
    for p in Path(__file__).parent.glob("*.py")
    if p.stem not in {"__init__"}
]

__all__ = MODULES


def init_all(app: Client) -> None:
    """Register all handlers on the provided ``Client`` instance."""
    for name in MODULES:
        module = import_module(f".{name}", __name__)
        init = getattr(module, "init", None)
        if callable(init):
            init(app)
