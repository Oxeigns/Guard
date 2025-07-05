# handlers/__init__.py

from . import admin, filters, callbacks, logging, broadcast, general

MODULES = [admin, filters, callbacks, logging, broadcast, general]

def register_all(app):
    for module in MODULES:
        if hasattr(module, "register"):
            try:
                module.register(app)
                print(f"✅ Registered: {module.__name__.split('.')[-1]}.py")
            except Exception as e:
                print(f"❌ Failed to register {module.__name__.split('.')[-1]}: {e}")
