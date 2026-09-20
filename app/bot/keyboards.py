"""Telegram keyboards for the initial user experience."""

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
