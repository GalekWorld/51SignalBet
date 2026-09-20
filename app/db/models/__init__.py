"""Persistence models grouped by domain."""

from app.db.models.alerts import AlertEvent, AlertRule
from app.db.models.audit import AuditLog
from app.db.models.bankroll import Bankroll, BankrollTransaction
from app.db.models.bets import BetRecord
from app.db.models.favorites import Favorite
from app.db.models.odds import Bookmaker, OddsSnapshot
from app.db.models.payments import PaymentEvent
from app.db.models.public_picks import PublishedPick
from app.db.models.settlements import SettlementEvent
from app.db.models.sports import Event, League, Player, Sport, Team
from app.db.models.subscriptions import Subscription
from app.db.models.users import User

__all__ = [
    "AlertEvent",
    "AlertRule",
    "AuditLog",
    "Bankroll",
    "BankrollTransaction",
    "BetRecord",
    "Bookmaker",
    "Event",
    "Favorite",
    "League",
    "OddsSnapshot",
    "PaymentEvent",
    "Player",
    "PublishedPick",
    "SettlementEvent",
    "Sport",
    "Subscription",
    "Team",
    "User",
]
