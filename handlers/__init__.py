"""Register all bot handlers."""

from pyrogram import Client

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
    general.register(app)
    admin.register(app)
    settings.register(app)
    custom_filters.register(app)
    callbacks.register(app)
    ping.register(app)
    msg_logging.register(app)
