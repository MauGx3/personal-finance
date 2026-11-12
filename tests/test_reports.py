from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.analytics.reports import income_by_month, realized_by_month, value_history
from apps.data_sources.models import FxRate, PriceQuote

pytestmark = pytest.mark.django_db


def test_realized_by_month_groups_sales(portfolio, petr4, aapl, trade):
    trade(petr4, "BUY", "2024-01-10", 100, 20)
    trade(petr4, "SELL", "2024-03-05", 10, 30)
    trade(petr4, "SELL", "2024-03-20", 10, 25, fees=5)
    trade(petr4, "SELL", "2024-04-02", 10, 15)
    trade(aapl, "SELL", "2024-03-01", 1, 100)  # inconsistent ledger: left out

    rows = realized_by_month([portfolio])

    assert [(r.month, r.asset_class, r.currency, r.sales, r.gain) for r in rows] == [
        (date(2024, 4, 1), "STOCK", "BRL", Decimal("150"), Decimal("-50")),
        (date(2024, 3, 1), "STOCK", "BRL", Decimal("545"), Decimal("145")),
    ]
    assert rows[0].asset_class_label == "Stock"


def test_income_by_month(portfolio, petr4, trade):
    trade(petr4, "DIVIDEND", "2024-03-05", amount=10)
    trade(petr4, "DIVIDEND", "2024-03-25", amount=5)
    trade(petr4, "JCP", "2024-03-25", amount=2)
    rows = income_by_month([portfolio])
    assert {(r.kind, r.amount) for r in rows} == {
        ("DIVIDEND", Decimal("15")),
        ("JCP", Decimal("2")),
    }


def test_value_history_tracks_quantity_price_and_fx(portfolio, petr4, aapl, trade):
    today = timezone.localdate()
    d = lambda n: today - timedelta(days=n)  # noqa: E731
    trade(petr4, "BUY", d(10).isoformat(), 100, 20)
    trade(aapl, "BUY", d(6).isoformat(), 10, 100)
    trade(petr4, "SELL", d(2).isoformat(), 50, 30)
    PriceQuote.objects.create(asset=petr4, day=d(8), close=Decimal("25"))
    PriceQuote.objects.create(asset=petr4, day=d(3), close=Decimal("30"))
    FxRate.objects.create(base="USD", quote="BRL", day=d(4), rate=Decimal("5"))

    history = dict(value_history([portfolio]))

    assert history[d(10)] == Decimal("2000")  # no close yet: trade price
    assert history[d(8)] == Decimal("2500")
    assert history[d(6)] == Decimal("7500")  # + 10 AAPL * 100 * 5 (oldest rate)
    assert history[d(3)] == Decimal("8000")
    assert history[today] == Decimal("6500")  # 50 * 30 + 5000
    assert len(history) == 11


def test_value_history_is_empty_without_transactions(portfolio):
    assert value_history([portfolio]) == []


def test_value_history_is_downsampled(portfolio, petr4, trade):
    trade(petr4, "BUY", (timezone.localdate() - timedelta(days=1000)).isoformat(), 1, 10)
    history = value_history([portfolio], max_points=50)
    assert 50 <= len(history) <= 52
    assert history[-1][0] == timezone.localdate()
