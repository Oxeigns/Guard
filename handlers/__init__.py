from pyrogram import Client

from . import echo, admin, broadcast, biomode, approval, longmode, sudo, filters as guard_filters


def register_handlers(app: Client):
    for module in (echo, admin, broadcast, biomode, approval, longmode, sudo, guard_filters):
        if hasattr(module, 'register'):
            module.register(app)
