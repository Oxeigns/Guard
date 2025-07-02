from pyrogram import Client

from . import echo, admin, broadcast, biomode, approval


def register_handlers(app: Client):
    for module in (echo, admin, broadcast, biomode, approval):
        if hasattr(module, 'register'):
            module.register(app)
