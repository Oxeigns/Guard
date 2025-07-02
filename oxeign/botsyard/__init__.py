from pyrogram import Client

from . import (
    bot,
    admin,
    broadcast,
    biomode,
    approval,
    longmode,
    sudo,
    filters as guard_filters,
    welcome,
    blacklist,
    autodelete,
)


def register_handlers(app: Client):
    for module in (
        bot,
        admin,
        broadcast,
        biomode,
        approval,
        longmode,
        sudo,
        guard_filters,
        welcome,
        blacklist,
        autodelete,
    ):
        if hasattr(module, "register"):
            module.register(app)
