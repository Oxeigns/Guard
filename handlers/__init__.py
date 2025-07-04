# 📁 File: handlers/__init__.py

from . import (
    commands,
    approval,
    menu,
    panel,
    autodelete,
    message_logger,
    biofilter,
)

def init_all(bot):
    """
    Register all command and message handlers to the bot.
    Each module must implement a `register(bot)` function.
    """
    commands.register(bot)
    approval.register(bot)
    menu.register(bot)
    panel.register(bot)
    autodelete.register(bot)
    message_logger.register(bot)
    biofilter.register(bot)
