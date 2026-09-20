"""Telegram handlers delegating work to application services."""

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.bot.keyboards import main_menu_keyboard
from app.services.user_service import UserService

router = Router(name="core")


def build_start_handler(user_service: UserService) -> object:
    """Create a start handler with an injected user service."""

    @router.message(CommandStart())
    async def start(message: Message) -> None:
        if message.from_user is None:
            return
        await user_service.register_telegram_user(
            telegram_user_id=message.from_user.id,
            username=message.from_user.username,
            language=message.from_user.language_code,
            timezone_name=None,
        )
        await message.answer(
            "Bienvenido. Selecciona una opción:",
            reply_markup=main_menu_keyboard(),
        )

    return start
