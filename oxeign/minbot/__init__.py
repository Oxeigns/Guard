from pyrogram import Client

from . import start, panel, biofilter, autodelete, grouptrack


def register_handlers(app: Client):
    for module in (start, panel, biofilter, autodelete, grouptrack):
        if hasattr(module, "register"):
            module.register(app)
