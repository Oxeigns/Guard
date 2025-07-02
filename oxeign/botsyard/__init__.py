from pyrogram import Client

from . import (
    bot,
    admin,
    broadcast,
    biomode,
    approval,
    longmode,
    sudo,
    grouptrack,
    filters as guard_filters,
    welcome,
    blacklist,
    autodelete,
    status,
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
        grouptrack,
        guard_filters,
        welcome,
        blacklist,
        autodelete,
        status,
    ):
        if hasattr(module, "register"):
            module.register(app)
