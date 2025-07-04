"""Register all bot handlers."""

from pyrogram import Client

# Import the actual handler modules. The file names use the
# ``bots_`` prefix, so import them explicitly rather than relying on
# implicit names that don't exist. Without these explicit imports the
# application fails to start with ``ImportError`` because modules like
# ``admin`` or ``callbacks`` are not found.
from . import (
    bots_admin as admin,
    bots_callbacks as callbacks,
    bots_filters as msg_filters,
    bots_general as general,
    bots_logging as msg_logging,
    bots_ping as ping,
    bots_settings as settings,
)


def register_all(app: Client) -> None:
    general.register(app)
    admin.register(app)
    settings.register(app)
    msg_filters.register(app)
    callbacks.register(app)
    ping.register(app)
    msg_logging.register(app)
