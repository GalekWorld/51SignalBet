"""Worker process entry point.

The production scheduler can invoke the idempotent jobs from this process. The
entry point intentionally remains quiet when no provider key is configured.
"""

import asyncio
import logging

from app.core.config import get_settings


async def run() -> None:
    logging.basicConfig(level=get_settings().log_level)
    logging.getLogger(__name__).info("worker ready; scheduler integration is configuration-driven")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(run())
