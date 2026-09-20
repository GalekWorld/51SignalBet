"""Telegram keyboards for the initial user experience."""

from uuid import UUID

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Build the initial menu without embedding business logic in handlers."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⚽ Partidos de hoy", callback_data="events:today")],
            [InlineKeyboardButton(text="🔥 Oportunidades", callback_data="opportunities:list")],
            [InlineKeyboardButton(text="🔎 Buscar partido", callback_data="events:search")],
            [InlineKeyboardButton(text="💰 Mi banca", callback_data="bankroll:home")],
            [InlineKeyboardButton(text="📈 Mis estadísticas", callback_data="stats:home")],
            [InlineKeyboardButton(text="🔔 Alertas", callback_data="alerts:home")],
            [InlineKeyboardButton(text="⚙️ Ajustes", callback_data="settings:home")],
        ]
    )


def event_keyboard(event_id: UUID, *, favorite: bool = False) -> InlineKeyboardMarkup:
    """Actions available from one event."""

    favorite_text = "☆ Quitar favorito" if favorite else "☆ Añadir favorito"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💸 Cuotas", callback_data=f"odds:{event_id}"),
                InlineKeyboardButton(text="📊 Mercados", callback_data=f"markets:{event_id}"),
            ],
            [
                InlineKeyboardButton(text="🔥 Oportunidades", callback_data=f"value:{event_id}"),
                InlineKeyboardButton(text=favorite_text, callback_data=f"favorite:{event_id}"),
            ],
            [InlineKeyboardButton(text="🔔 Crear alerta", callback_data=f"alert:{event_id}")],
            [InlineKeyboardButton(text="↩️ Partidos de hoy", callback_data="events:today")],
        ]
    )


def market_keyboard(event_id: UUID, markets: list[str]) -> InlineKeyboardMarkup:
    """Bounded list of persisted markets."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=market[:45], callback_data=f"market:{event_id}:{index}")]
            for index, market in enumerate(markets)
        ]
        + [[InlineKeyboardButton(text="↩️ Evento", callback_data=f"event:{event_id}")]]
    )
