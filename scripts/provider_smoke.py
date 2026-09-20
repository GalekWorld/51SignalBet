"""Explicit real-provider smoke test; never runs in standard CI."""

import asyncio
import sys

from app.core.config import get_settings
from app.providers.odds_api import OddsApiProvider


async def main() -> int:
    key = get_settings().odds_api_key
    if not key:
        print("ODDS_API_KEY is required for the real provider smoke test", file=sys.stderr)
        return 2
    async with OddsApiProvider(key, max_retries=1) as provider:
        sports = await provider.list_sports()
    print(f"provider smoke ok: {len(sports)} sports")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
