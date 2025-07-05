from . import admin, moderation, callbacks, logging, broadcast, general

MODULES = [admin, moderation, callbacks, logging, broadcast, general]

def register_all(app):
    for module in MODULES:
        if hasattr(module, "register"):
            module.register(app)
