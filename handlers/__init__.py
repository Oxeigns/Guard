"""Register all bot handlers."""

from . import approval, autodelete, biofilter, commands, menu, panel, message_logger


def init_all(app):
    """Register all handlers to the given Pyrogram client."""
    approval.register(app)
    autodelete.register(app)
    biofilter.register(app)
    commands.register(app)
    menu.register(app)
    panel.register(app)
    message_logger.register(app)
