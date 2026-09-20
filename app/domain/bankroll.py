"""Virtual bankroll concepts."""

from enum import StrEnum


class BankrollTransactionType(StrEnum):
    """Ledger transaction categories."""

    INITIAL = "initial"
    BET_STAKE = "bet_stake"
    WIN = "win"
    LOSS = "loss"
    VOID = "void"
    ADJUSTMENT = "adjustment"
    VIRTUAL_DEPOSIT = "virtual_deposit"
    VIRTUAL_WITHDRAWAL = "virtual_withdrawal"
