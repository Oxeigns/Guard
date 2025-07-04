"""Register all bot handlers."""

from pyrogram import Client
import logging

logger = logging.getLogger(__name__)

# Explicit imports to avoid shadowing
from . import (
    admin,
    callbacks,
    filters as custom_filters,
    general,
    logging as msg_logging,
    ping,
    settings,
)


def register_all(app: Client) -> None:
    logger.info("Registering general handlers")
    general.register(app)
    logger.info("Registering admin handlers")
    admin.register(app)
    logger.info("Registering settings handlers")
    settings.register(app)
    logger.info("Registering custom filters")
    custom_filters.register(app)
    logger.info("Registering callback handlers")
    callbacks.register(app)
    logger.info("Registering ping handlers")
    ping.register(app)
    logger.info("Registering message logging handlers")
    msg_logging.register(app)
