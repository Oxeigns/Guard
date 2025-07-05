from . import admin, filters, callbacks, logging, broadcast, general, panels

MODULES = [admin, filters, callbacks, logging, broadcast, general, panels]


def register_all(app) -> None:
    """Register all handler modules with the given Pyrogram client."""
    for module in MODULES:
        if hasattr(module, "register"):
            try:
                module.register(app)
                print(f"✅ Registered: {module.__name__.split('.')[-1]}.py")
            except Exception as exc:  # noqa: BLE001
                print(f"❌ Failed to register {module.__name__.split('.')[-1]}: {exc}")
