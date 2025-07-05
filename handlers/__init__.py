from . import admin, filters, callbacks, logging, broadcast, general

MODULES = [admin, filters, callbacks, logging, broadcast, general]

def register_all(app):
    for module in MODULES:
        if hasattr(module, "register"):
            module.register(app)
