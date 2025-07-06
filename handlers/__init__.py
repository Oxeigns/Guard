import logging

logger = logging.getLogger(__name__)

from . import (
    admin,
    filters,
    callbacks,
    logger as log_module,  # 🟡 renamed to avoid shadowing
    broadcast,
    general,
    panels,
)

MODULES = [admin, filters, callbacks, log_module, broadcast, general, panels]


def register_all(app):
    logger.info("🔁 Registering all handler modules...")
    for module in MODULES:
        if hasattr(module, "register"):
            try:
                module.register(app)
                logger.info(f"✅ Registered: {module.__name__.split('.')[-1]}.py")
            except Exception as e:
                logger.error(f"❌ Failed to register {module.__name__.split('.')[-1]}: {e}")
        else:
            logger.warning(f"⚠️ Skipped: {module.__name__.split('.')[-1]}.py — no register() function")
    logger.info("✅ All modules registered.")
