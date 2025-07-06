# handlers/__init__.py

from . import (
    admin,
    filters,
    callbacks,
    logger,  # ✅ renamed from logging.py to avoid name conflict
    broadcast,
    general,
    panels,
)

MODULES = [admin, filters, callbacks, logger, broadcast, general, panels]

def register_all(app):
    for module in MODULES:
        if hasattr(module, "register"):
            try:
                module.register(app)
                print(f"✅ Registered: {module.__name__.split('.')[-1]}.py")
            except Exception as e:
                print(f"❌ Failed to register {module.__name__.split('.')[-1]}: {e}")
        else:
            print(f"⚠️ Skipped: {module.__name__.split('.')[-1]}.py — no register() function")
