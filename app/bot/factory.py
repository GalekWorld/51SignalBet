"""Telegram bot construction without starting polling at import time."""

from aiogram import Bot, Dispatcher

from app.bot.event_handlers import router as event_router
from app.bot.handlers import router as core_router


def create_dispatcher() -> Dispatcher:
    """Build a dispatcher with the core router registered."""

    dispatcher = Dispatcher()
    dispatcher.include_router(core_router)
    dispatcher.include_router(event_router)
    return dispatcher


def create_bot(token: str) -> Bot:
    """Create a Bot instance; callers own its lifecycle."""

    if not token:
        raise ValueError("Telegram bot token is required")
    return Bot(token=token)
