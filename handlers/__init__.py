import logging
from pyrogram import Client

from . import approval, autodelete, biofilter, commands, menu, message_logger, panel

logger = logging.getLogger(__name__)

ALL_MODULES = [
    approval,
    autodelete,
    biofilter,
    commands,
    menu,
    message_logger,
    panel,
]


def init_all(app: Client) -> None:
    """Register all handlers to the given Pyrogram client."""
    for module in ALL_MODULES:
        if hasattr(module, "register"):
            module.register(app)
            logger.debug("Registered handlers from %s", module.__name__)
