"""Register all bot handlers."""

from pyrogram import Client
import logging as py_logging

# Import all submodules so their decorators (if any) execute.
from . import (
    ping,
    admin,
    callbacks,
    filters,
    general,
    logging as msg_logging,
    settings,
)

logger = py_logging.getLogger(__name__)


def register_all(app: Client) -> None:
    """Register each handler module with the provided ``Client``."""
    logger.info("Registering handlers")

    ping.register(app)
    admin.register(app)
    callbacks.register(app)
    filters.register(app)
    general.register(app)
    msg_logging.register(app)
    settings.register(app)
