"""Register all bot handlers."""

from pyrogram import Client

from . import (
    admin,
    callbacks,
    filters as msg_filters,
    general,
    logging as msg_logging,
    ping,
    settings,
)


def register_all(app: Client) -> None:
    general.register(app)
    admin.register(app)
    settings.register(app)
    msg_filters.register(app)
    callbacks.register(app)
    ping.register(app)
    msg_logging.register(app)
