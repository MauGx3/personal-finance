"""Position maths: turn a ledger of transactions into a position.

Pure functions, no database access, so the rules are easy to test and reuse.
Cost basis uses the weighted average price ("preço médio"), which is how
Brazilian brokers and the tax authority track it.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Protocol

from apps.core.money import ZERO


class PositionError(ValueError):
    """The ledger is inconsistent (for example, selling more than is held)."""


class LedgerEntry(Protocol):
    """What the calculator needs from a transaction."""

    kind: str
    trade_date: date
    quantity: Decimal
    price: Decimal
    fees: Decimal
    amount: Decimal


BUY, SELL, DIVIDEND, JCP, INCOME, SPLIT, BONUS = (
    "BUY",
    "SELL",
    "DIVIDEND",
    "JCP",
    "INCOME",
    "SPLIT",
    "BONUS",
)
INCOME_KINDS = frozenset({DIVIDEND, JCP, INCOME})
# Order applied when several entries share a date: corporate actions first,
# then buys, then sells, so a same-day buy and sell never looks like a short.
_SAME_DAY_ORDER = {SPLIT: 0, BONUS: 1, BUY: 2, SELL: 3}


@dataclass(frozen=True)
class RealizedSale:
    """Outcome of one sale, the building block of gain reports."""

    trade_date: date
    quantity: Decimal
    proceeds: Decimal  # net of fees
    cost: Decimal
    gain: Decimal


@dataclass
class Position:
    quantity: Decimal = ZERO
    average_price: Decimal = ZERO
    realized_gain: Decimal = ZERO
    income: Decimal = ZERO
    first_trade: date | None = None
    last_trade: date | None = None
    sales: list[RealizedSale] = field(default_factory=list)

    @property
    def cost_basis(self) -> Decimal:
        return self.quantity * self.average_price


def sort_ledger[T: LedgerEntry](entries: Iterable[T]) -> list[T]:
    return sorted(entries, key=lambda e: (e.trade_date, _SAME_DAY_ORDER.get(e.kind, 9)))


def compute_position(entries: Iterable[LedgerEntry]) -> Position:
    """Replay ``entries`` in date order and return the resulting position.

    Rules:
        BUY      adds shares; fees are part of the cost.
        SELL     removes shares at the current average price; fees reduce the
                 proceeds. The average price of what remains is unchanged.
        SPLIT    ``quantity`` is the ratio of new to old shares (2 for a
                 2-for-1 split, 0.1 for a 10-to-1 reverse split).
        BONUS    adds ``quantity`` shares at ``price`` cost per share.
        DIVIDEND / JCP / INCOME add ``amount`` to income, shares unchanged.

    Raises:
        PositionError: on a sale larger than the position, or a bad split ratio.
    """
    position = Position()
    for entry in sort_ledger(entries):
        if entry.kind in INCOME_KINDS:
            position.income += entry.amount
            continue

        if entry.kind in (BUY, BONUS):
            cost = entry.quantity * entry.price + entry.fees
            new_quantity = position.quantity + entry.quantity
            if new_quantity > 0:
                position.average_price = (position.cost_basis + cost) / new_quantity
            position.quantity = new_quantity
        elif entry.kind == SELL:
            if entry.quantity > position.quantity:
                raise PositionError(
                    f"Sale of {entry.quantity} on {entry.trade_date} exceeds "
                    f"the {position.quantity} held."
                )
            cost = entry.quantity * position.average_price
            proceeds = entry.quantity * entry.price - entry.fees
            position.realized_gain += proceeds - cost
            position.sales.append(
                RealizedSale(entry.trade_date, entry.quantity, proceeds, cost, proceeds - cost)
            )
            position.quantity -= entry.quantity
            if position.quantity == 0:
                position.average_price = ZERO
        elif entry.kind == SPLIT:
            if entry.quantity <= 0:
                raise PositionError(f"Split ratio must be positive, got {entry.quantity}.")
            position.quantity *= entry.quantity
            position.average_price /= entry.quantity
        else:
            raise PositionError(f"Unknown transaction kind: {entry.kind!r}")

        position.first_trade = position.first_trade or entry.trade_date
        position.last_trade = entry.trade_date
    return position
