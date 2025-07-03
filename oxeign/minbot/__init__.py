from pyrogram import Client

from . import start, panel, biofilter, autodelete, grouptrack, approvecmds


def register_handlers(app: Client):
    for module in (start, panel, biofilter, autodelete, grouptrack, approvecmds):
        if hasattr(module, "register"):
            module.register(app)
