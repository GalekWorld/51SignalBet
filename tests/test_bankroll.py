from decimal import Decimal

from app.db.base import Base
from app.domain.bankroll import BankrollTransactionType
from app.services.bankroll import InvalidBankrollOperation


def test_bankroll_has_all_ledger_transaction_types() -> None:
    assert {item.value for item in BankrollTransactionType} == {
        "initial",
        "bet_stake",
        "win",
        "loss",
        "void",
        "adjustment",
        "virtual_deposit",
        "virtual_withdrawal",
    }


def test_bankroll_tables_are_registered() -> None:
    assert {"bankrolls", "bankroll_transactions"} <= set(Base.metadata.tables)
    assert Decimal("10.00") + Decimal("2.50") == Decimal("12.50")
    assert issubclass(InvalidBankrollOperation, ValueError)
