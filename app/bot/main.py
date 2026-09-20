"""Telegram polling process entry point."""

import asyncio
from decimal import Decimal
from typing import cast
from uuid import UUID

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.statistics import SettledBet, StatisticsService
from app.bot.keyboards import event_keyboard, main_menu_keyboard, market_keyboard
from app.core.config import get_settings
from app.db.models import AlertRule, BetRecord, Favorite, User
from app.db.session import create_session_factory, dispose_engine
from app.domain.alerts import AlertMetric, AlertOperator
from app.domain.bets import BetStatus
from app.domain.favorites import FavoriteType
from app.services.bankroll import BankrollService
from app.services.event_detail import EventDetailService, EventNotFound
from app.services.favorites import FavoriteService
from app.services.odds_comparison import BookmakerQuote, OddsComparisonService
from app.services.telegram_market import QuoteView, TelegramMarketService
from app.services.today_events import TodayEventsService
from app.services.user_service import UserService


async def run() -> None:
    token = get_settings().telegram_bot_token
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required for the bot process")
    bot = Bot(token)
    dispatcher = Dispatcher()
    sessions = create_session_factory()

    async def get_user(session: AsyncSession, telegram_user_id: int) -> User | None:
        return cast(
            User | None,
            await session.scalar(select(User).where(User.telegram_user_id == telegram_user_id)),
        )

    async def render_event(callback: CallbackQuery, event_id: UUID) -> None:
        if callback.from_user is None or not isinstance(callback.message, Message):
            return
        async with sessions() as session:
            user = await get_user(session, callback.from_user.id)
            favorite = bool(
                user
                and await session.scalar(
                    select(Favorite).where(
                        Favorite.user_id == user.id,
                        Favorite.favorite_type == FavoriteType.EVENT,
                        Favorite.target_id == event_id,
                    )
                )
            )
            timezone_name = await UserService(session).get_timezone(callback.from_user.id)
            detail = await EventDetailService(session).get(event_id, timezone_name=timezone_name)
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
        await callback.message.edit_text(
            "\n".join(lines), reply_markup=event_keyboard(event_id, favorite=favorite)
        )

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
                await EventDetailService(session).get(event_id, timezone_name=timezone_name)
        except (ValueError, EventNotFound):
            await callback.answer("No se encontró el partido", show_alert=True)
            return
        await callback.answer()
        await render_event(callback, event_id)

    @dispatcher.callback_query(F.data.startswith("event:"))
    async def back_to_event(callback: CallbackQuery) -> None:
        if callback.data is None:
            return
        try:
            event_id = UUID(callback.data.removeprefix("event:"))
            await callback.answer()
            await render_event(callback, event_id)
        except (ValueError, EventNotFound):
            await callback.answer("No se encontró el evento", show_alert=True)

    @dispatcher.callback_query(F.data.startswith("odds:"))
    async def odds(callback: CallbackQuery) -> None:
        if callback.data is None or not isinstance(callback.message, Message):
            return
        try:
            event_id = UUID(callback.data.removeprefix("odds:"))
            async with sessions() as session:
                quotes = await TelegramMarketService(session).quotes(event_id)
            if not quotes:
                text = "💸 No hay cuotas disponibles para este evento."
            else:
                best: dict[tuple[str, str], QuoteView] = {}
                for quote in quotes:
                    key = (quote.market, quote.selection)
                    if key not in best or quote.odds > best[key].odds:
                        best[key] = quote
                lines = ["💸 Cuotas disponibles", ""]
                for quote in list(best.values())[:25]:
                    lines.append(
                        f"{quote.market[:28]} · {quote.selection[:24]}: {quote.odds} ({quote.bookmaker})"
                    )
                text = "\n".join(lines)
            await callback.answer()
            await callback.message.edit_text(text, reply_markup=event_keyboard(event_id))
        except ValueError:
            await callback.answer("Cuotas no disponibles", show_alert=True)

    @dispatcher.callback_query(F.data.startswith("markets:"))
    async def markets(callback: CallbackQuery) -> None:
        if callback.data is None or not isinstance(callback.message, Message):
            return
        try:
            event_id = UUID(callback.data.removeprefix("markets:"))
            async with sessions() as session:
                values = await TelegramMarketService(session).markets(event_id)
            text = "📊 Mercados disponibles" if values else "📊 No hay mercados disponibles."
            await callback.answer()
            await callback.message.edit_text(text, reply_markup=market_keyboard(event_id, values))
        except ValueError:
            await callback.answer("Mercados no disponibles", show_alert=True)

    @dispatcher.callback_query(F.data.startswith("market:"))
    async def market_detail(callback: CallbackQuery) -> None:
        if callback.data is None or not isinstance(callback.message, Message):
            return
        try:
            _, event_value, index_value = callback.data.split(":", 2)
            event_id = UUID(event_value)
            index = int(index_value)
            async with sessions() as session:
                service = TelegramMarketService(session)
                market_names = await service.markets(event_id)
                market = market_names[index]
                market_quotes = await service.quotes(event_id, market=market)
            by_selection: dict[str, list[QuoteView]] = {}
            for quote in market_quotes:
                by_selection.setdefault(quote.selection, []).append(quote)
            comparison = []
            compare_service = OddsComparisonService()
            for selection, values in by_selection.items():
                result = compare_service.compare(
                    selection,
                    [BookmakerQuote(q.bookmaker, q.odds) for q in values],
                )
                comparison.append(
                    f"{selection}: mejor {result.best_odds} ({result.best_bookmaker}), peor {result.worst_odds}, media {result.average_odds:.2f}, bookmakers {result.bookmaker_count}"
                )
            text = f"📊 {market}\n\n" + ("\n".join(comparison[:20]) or "Sin cuotas disponibles.")
            await callback.answer()
            await callback.message.edit_text(text, reply_markup=event_keyboard(event_id))
        except (ValueError, IndexError):
            await callback.answer("Mercado no disponible", show_alert=True)

    @dispatcher.callback_query(F.data.startswith("value:"))
    async def value(callback: CallbackQuery) -> None:
        if callback.data is None or not isinstance(callback.message, Message):
            return
        try:
            event_id = UUID(callback.data.removeprefix("value:"))
            async with sessions() as session:
                opportunities = await TelegramMarketService(session).opportunities(event_id)
            if not opportunities:
                text = "🔥 No se han detectado oportunidades que cumplan los criterios actuales."
            else:
                text = "🔥 Oportunidades\n\n" + "\n".join(
                    f"{item.market} · {item.selection}: {item.best_odds} ({item.best_bookmaker}), edge {item.edge:.2%}, EV {item.expected_value:.2%}"
                    for item in opportunities[:10]
                )
            await callback.answer()
            await callback.message.edit_text(text, reply_markup=event_keyboard(event_id))
        except ValueError:
            await callback.answer("Oportunidades no disponibles", show_alert=True)

    @dispatcher.callback_query(F.data.startswith("favorite:"))
    async def favorite(callback: CallbackQuery) -> None:
        if callback.data is None or callback.from_user is None:
            return
        try:
            event_id = UUID(callback.data.removeprefix("favorite:"))
            async with sessions() as session:
                user = await get_user(session, callback.from_user.id)
                if user is None:
                    await callback.answer("Usa /start primero", show_alert=True)
                    return
                service = FavoriteService(session)
                existing = await session.scalar(
                    select(Favorite).where(
                        Favorite.user_id == user.id,
                        Favorite.favorite_type == FavoriteType.EVENT,
                        Favorite.target_id == event_id,
                    )
                )
                if existing:
                    await service.remove(user.id, FavoriteType.EVENT, event_id)
                    message = "Evento quitado de favoritos"
                else:
                    await service.add(user.id, FavoriteType.EVENT, event_id)
                    message = "Evento guardado en favoritos"
            await callback.answer(message)
            await render_event(callback, event_id)
        except ValueError:
            await callback.answer("Favorito no válido", show_alert=True)

    @dispatcher.callback_query(F.data.startswith("alert:"))
    async def alert(callback: CallbackQuery) -> None:
        if callback.data is None or callback.from_user is None:
            return
        try:
            event_id = UUID(callback.data.removeprefix("alert:"))
            async with sessions() as session:
                user = await get_user(session, callback.from_user.id)
                if user is None:
                    await callback.answer("Usa /start primero", show_alert=True)
                    return
                rules = list(
                    await session.scalars(select(AlertRule).where(AlertRule.user_id == user.id))
                )
                filters = {"event_id": str(event_id)}
                rule = next(
                    (
                        item
                        for item in rules
                        if item.metric == AlertMetric.EDGE and item.filters == filters
                    ),
                    None,
                )
                if rule is None:
                    rule = AlertRule(
                        user_id=user.id,
                        metric=AlertMetric.EDGE,
                        operator=AlertOperator.GREATER_EQUAL,
                        threshold=Decimal("0.05"),
                        filters=filters,
                        cooldown_seconds=3600,
                        enabled=True,
                    )
                    session.add(rule)
                    await session.commit()
            await callback.answer("Alerta creada para este evento")
        except ValueError:
            await callback.answer("Alerta no válida", show_alert=True)

    @dispatcher.callback_query(F.data == "bankroll:home")
    async def bankroll(callback: CallbackQuery) -> None:
        if callback.from_user is None or not isinstance(callback.message, Message):
            return
        async with sessions() as session:
            user = await get_user(session, callback.from_user.id)
            if user is None:
                await callback.answer("Usa /start primero", show_alert=True)
                return
            service = BankrollService(session)
            bankroll_record = await service.get_or_create(user.id)
            await session.commit()
            balance = await service.balance(bankroll_record.id)
        await callback.answer()
        await callback.message.edit_text(
            f"💰 Mi banca\n\nSaldo virtual: {balance:.2f} EUR\nNo hay dinero real involucrado.",
            reply_markup=main_menu_keyboard(),
        )

    @dispatcher.callback_query(F.data == "stats:home")
    async def stats(callback: CallbackQuery) -> None:
        if callback.from_user is None or not isinstance(callback.message, Message):
            return
        async with sessions() as session:
            user = await get_user(session, callback.from_user.id)
            bets = (
                list(await session.scalars(select(BetRecord).where(BetRecord.user_id == user.id)))
                if user
                else []
            )
        settled = [
            BetRecord
            for BetRecord in bets
            if str(BetRecord.status)
            in {BetStatus.WON, BetStatus.LOST, BetStatus.VOID, BetStatus.PUSH}
        ]
        if not settled:
            text = "📈 Estadísticas\n\nTodavía no hay apuestas registradas."
        else:
            values = [
                SettledBet(
                    item.placed_at, str(item.status), item.odds, item.stake, market=item.market
                )
                for item in settled
            ]
            result = StatisticsService().calculate(values)
            text = f"📈 Estadísticas\n\nApuestas: {result.bets}\nGanadas: {result.wins}\nPerdidas: {result.losses}\nProfit: {result.profit:.2f}\nROI: {result.roi:.2%}\nYield: {result.yield_value:.2%}"
        await callback.answer()
        await callback.message.edit_text(text, reply_markup=main_menu_keyboard())

    @dispatcher.callback_query(
        F.data.in_({"opportunities:list", "alerts:home", "events:search", "settings:home"})
    )
    async def simple_menu_status(callback: CallbackQuery) -> None:
        await callback.answer(
            "Esta vista se completa desde un evento o todavía no tiene datos.", show_alert=True
        )

    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()
        await dispose_engine()


if __name__ == "__main__":
    asyncio.run(run())
