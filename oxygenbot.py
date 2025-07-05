"""Entry point for the bot process."""

import asyncio
import threading
from mybot.main import main
import os
from web import app as web_app


def _start_web() -> None:
    """Run the small Flask server used for platform health checks."""
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Run the lightweight Flask web server in a separate thread so platforms
    # expecting an open port consider the service healthy.
    thread = threading.Thread(target=_start_web, daemon=True)
    thread.start()
    asyncio.run(main())
