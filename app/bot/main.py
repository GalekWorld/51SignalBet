"""Telegram polling process entry point."""

import asyncio
from uuid import UUID

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.bot.keyboards import main_menu_keyboard
from app.core.config import get_settings
from app.db.session import create_session_factory, dispose_engine
from app.services.event_detail import EventDetailService, EventNotFound
from app.services.today_events import TodayEventsService
from app.services.user_service import UserService


async def run() -> None:
    token = get_settings().telegram_bot_token
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required for the bot process")
    bot = Bot(token)
    dispatcher = Dispatcher()
    sessions = create_session_factory()

    @dispatcher.message(CommandStart())
    async def start(message: Message) -> None:
        if message.from_user is None:
            return
        async with sessions() as session:
            await UserService(session).register_telegram_user(
                telegram_user_id=message.from_user.id,
                username=message.from_user.username,
                language=message.from_user.language_code,
                timezone_name=None,
            )
        await message.answer(
            "Bienvenido. Selecciona una opción:", reply_markup=main_menu_keyboard()
        )

    @dispatcher.callback_query(F.data == "events:today")
    async def today(callback: CallbackQuery) -> None:
        if callback.from_user is None or not isinstance(callback.message, Message):
            return
        async with sessions() as session:
            user_service = UserService(session)
            timezone_name = await user_service.get_timezone(callback.from_user.id)
            events = await TodayEventsService(session).list_today(timezone_name=timezone_name)
        if not events:
            await callback.message.edit_text("⚽ No hay partidos programados para hoy.")
        else:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"{event.home_team} vs {event.away_team}",
                            callback_data=f"events:detail:{event.id}",
                        )
                    ]
                    for event in events
                ]
            )
            await callback.message.edit_text("⚽ Partidos de hoy", reply_markup=keyboard)
        await callback.answer()

    @dispatcher.callback_query(F.data.startswith("events:detail:"))
    async def event_detail(callback: CallbackQuery) -> None:
        if (
            callback.from_user is None
            or not isinstance(callback.message, Message)
            or callback.data is None
        ):
            return
        try:
            event_id = UUID(callback.data.removeprefix("events:detail:"))
            async with sessions() as session:
                user_service = UserService(session)
                timezone_name = await user_service.get_timezone(callback.from_user.id)
                detail = await EventDetailService(session).get(
                    event_id, timezone_name=timezone_name
                )
        except (ValueError, EventNotFound):
            await callback.answer("No se encontró el partido", show_alert=True)
            return
        lines = [
            f"⚽ {detail.home_team} vs {detail.away_team}",
            f"🕒 {detail.start_time:%d/%m %H:%M}",
            f"🏷️ {detail.league or detail.sport}",
            f"📌 Estado: {detail.status}",
        ]
        if detail.home_score is not None and detail.away_score is not None:
            lines.append(f"📊 Resultado: {detail.home_score}-{detail.away_score}")
        if detail.venue:
            lines.append(f"📍 {detail.venue}")
        await callback.answer()
        await callback.message.edit_text("\n".join(lines))

    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()
        await dispose_engine()


if __name__ == "__main__":
    asyncio.run(run())
