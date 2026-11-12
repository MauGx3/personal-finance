from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import pytest

from apps.portfolios.services.positions import PositionError, compute_position


@dataclass
class Entry:
    kind: str
    trade_date: date
    quantity: Decimal = Decimal(0)
    price: Decimal = Decimal(0)
    fees: Decimal = Decimal(0)
    amount: Decimal = Decimal(0)


def entry(kind, day, quantity=0, price=0, fees=0, amount=0):
    return Entry(
        kind, date.fromisoformat(day), Decimal(str(quantity)), Decimal(str(price)),
        Decimal(str(fees)), Decimal(str(amount)),
    )  # fmt: skip


def test_empty_ledger_is_an_empty_position():
    position = compute_position([])
    assert position.quantity == 0
    assert position.first_trade is None


def test_buys_average_the_price_and_include_fees():
    position = compute_position(
        [entry("BUY", "2024-01-10", 100, 10, fees=5), entry("BUY", "2024-02-10", 100, 20, fees=5)]
    )
    assert position.quantity == 200
    assert position.average_price == Decimal("15.05")
    assert position.cost_basis == Decimal("3010")


def test_sale_realizes_gain_and_keeps_average_price():
    position = compute_position(
        [
            entry("BUY", "2024-01-10", 100, 10),
            entry("BUY", "2024-02-10", 100, 20),
            entry("SELL", "2024-03-10", 50, 30, fees=10),
        ]
    )
    assert position.quantity == 150
    assert position.average_price == Decimal("15")
    assert position.realized_gain == Decimal("740")  # 50*30 - 10 - 50*15
    assert [(s.proceeds, s.cost, s.gain) for s in position.sales] == [
        (Decimal("1490"), Decimal("750"), Decimal("740"))
    ]


def test_selling_everything_resets_the_average_price():
    position = compute_position(
        [
            entry("BUY", "2024-01-10", 10, 10),
            entry("SELL", "2024-02-10", 10, 8),
            entry("BUY", "2024-03-10", 10, 20),
        ]
    )
    assert position.realized_gain == Decimal("-20")
    assert position.average_price == Decimal("20")


def test_entries_are_replayed_in_date_order_with_buys_before_sells():
    position = compute_position(
        [entry("SELL", "2024-01-10", 10, 12), entry("BUY", "2024-01-10", 10, 10)]
    )
    assert position.quantity == 0
    assert position.realized_gain == Decimal("20")


def test_selling_more_than_held_is_an_error():
    with pytest.raises(PositionError, match="exceeds"):
        compute_position([entry("BUY", "2024-01-10", 10, 10), entry("SELL", "2024-02-10", 11, 10)])


def test_split_and_reverse_split_keep_the_cost_basis():
    split = compute_position([entry("BUY", "2024-01-10", 100, 40), entry("SPLIT", "2024-02-01", 2)])
    assert (split.quantity, split.average_price, split.cost_basis) == (200, 20, 4000)
    reverse = compute_position(
        [entry("BUY", "2024-01-10", 100, 4), entry("SPLIT", "2024-02-01", "0.1")]
    )
    assert (reverse.quantity, reverse.average_price) == (10, 40)
    with pytest.raises(PositionError):
        compute_position([entry("BUY", "2024-01-10", 100, 4), entry("SPLIT", "2024-02-01", 0)])


def test_bonus_shares_add_quantity_at_their_cost():
    position = compute_position(
        [entry("BUY", "2024-01-10", 100, 10), entry("BONUS", "2024-02-01", 10, 5)]
    )
    assert position.quantity == 110
    assert position.cost_basis == Decimal("1050")


def test_income_accumulates_without_touching_the_position():
    position = compute_position(
        [
            entry("BUY", "2024-01-10", 100, 10),
            entry("DIVIDEND", "2024-02-01", amount="12.34"),
            entry("JCP", "2024-03-01", amount="5.66"),
        ]
    )
    assert position.income == Decimal("18.00")
    assert position.quantity == 100
    assert position.last_trade == date(2024, 1, 10)


def test_unknown_kind_is_rejected():
    with pytest.raises(PositionError):
        compute_position([entry("GIFT", "2024-01-10", 1, 1)])
