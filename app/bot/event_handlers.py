"""Telegram handlers for the today's-events view."""

from uuid import UUID

from aiogram import Router
from aiogram.types import CallbackQuery, Message

from app.services.event_detail import EventDetailService, EventNotFound
from app.services.today_events import TodayEventsService
from app.services.user_service import UserService

router = Router(name="today-events")


def build_today_events_handler(service: TodayEventsService, user_service: UserService) -> object:
    """Create a callback handler backed by the today's-events use case."""

    @router.callback_query(lambda callback: callback.data == "events:today")
    async def today_events(callback: CallbackQuery) -> None:
        if callback.from_user is None or not isinstance(callback.message, Message):
            return
        timezone_name = await user_service.get_timezone(callback.from_user.id)
        events = await service.list_today(timezone_name=timezone_name)
        if not events:
            text = "⚽ No hay partidos programados para hoy."
        else:
            lines = ["⚽ Partidos de hoy", ""]
            for event in events:
                lines.append(f"• {event.start_time:%H:%M} — {event.home_team} vs {event.away_team}")
            text = "\n".join(lines)
        await callback.answer()
        await callback.message.edit_text(text)

    return today_events


def build_event_detail_handler(service: EventDetailService, user_service: UserService) -> object:
    """Create a callback handler for one event detail view."""

    @router.callback_query(
        lambda callback: bool(callback.data and callback.data.startswith("events:detail:"))
    )
    async def event_detail(callback: CallbackQuery) -> None:
        if (
            callback.from_user is None
            or not isinstance(callback.message, Message)
            or callback.data is None
        ):
            return
        try:
            event_id = UUID(callback.data.removeprefix("events:detail:"))
            timezone_name = await user_service.get_timezone(callback.from_user.id)
            detail = await service.get(event_id, timezone_name=timezone_name)
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

    return event_detail
