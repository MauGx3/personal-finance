from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.assets.models import Asset, AssetClass, Exchange, guess_asset_class, normalize_ticker
from apps.data_sources.models import FxRate, PriceQuote
from apps.portfolios.models import Holding, Portfolio, Transaction
from apps.portfolios.services.valuation import snapshot

pytestmark = pytest.mark.django_db


def test_ticker_normalization_and_class_guess():
    assert normalize_ticker(" petr4f ") == "PETR4"
    assert normalize_ticker("F", Exchange.NYSE) == "F"  # Ford is not a fractional ticker
    assert guess_asset_class("PETR4") == AssetClass.STOCK
    assert guess_asset_class("HGLG11") == AssetClass.FII
    assert guess_asset_class("AAPL34") == AssetClass.BDR
    assert guess_asset_class("AAPL", Exchange.NASDAQ) == AssetClass.STOCK


def test_quote_symbol_follows_the_exchange(petr4, aapl):
    assert petr4.quote_symbol == "PETR4.SA"
    assert aapl.quote_symbol == "AAPL"
    aapl.provider_symbol = "AAPL.MX"
    assert aapl.quote_symbol == "AAPL.MX"


def test_get_or_create_for_ticker_sets_defaults():
    asset, created = Asset.get_or_create_for_ticker("hglg11f")
    assert created
    assert (asset.ticker, asset.asset_class, asset.currency) == ("HGLG11", AssetClass.FII, "BRL")
    assert Asset.get_or_create_for_ticker("HGLG11") == (asset, False)


def test_first_portfolio_is_default_and_there_is_only_one(user):
    first = Portfolio.objects.create(user=user, name="A")
    second = Portfolio.objects.create(user=user, name="B", is_default=True)
    first.refresh_from_db()
    assert second.is_default and not first.is_default
    assert Portfolio.default_for(user) == second


def test_holding_follows_the_ledger(portfolio, petr4, trade):
    buy = trade(petr4, "BUY", "2024-01-10", 100, "25.50")
    holding = Holding.objects.get(portfolio=portfolio, asset=petr4)
    assert (holding.quantity, holding.average_price) == (100, Decimal("25.5"))

    trade(petr4, "SELL", "2024-02-10", 40, 30)
    trade(petr4, "DIVIDEND", "2024-03-01", amount="18.20")
    holding.refresh_from_db()
    assert holding.quantity == 60
    assert holding.realized_gain == Decimal("180.00")
    assert holding.income == Decimal("18.20")

    buy.quantity = 200
    buy.save()
    holding.refresh_from_db()
    assert holding.quantity == 160

    Transaction.objects.filter(portfolio=portfolio).delete()
    assert not Holding.objects.exists()


def test_inconsistent_ledger_is_flagged_not_raised(portfolio, petr4, trade):
    trade(petr4, "SELL", "2024-02-10", 40, 30)
    holding = Holding.objects.get(asset=petr4)
    assert "exceeds" in holding.ledger_error
    trade(petr4, "BUY", "2024-01-10", 100, 20)
    holding.refresh_from_db()
    assert holding.ledger_error == ""
    assert holding.quantity == 60


def test_transaction_validation(portfolio, petr4):
    with pytest.raises(ValidationError):
        Transaction(
            portfolio=portfolio, asset=petr4, kind="BUY", trade_date="2024-01-01"
        ).full_clean()
    with pytest.raises(ValidationError):
        Transaction(
            portfolio=portfolio, asset=petr4, kind="DIVIDEND", trade_date="2024-01-01"
        ).full_clean()


def test_snapshot_values_in_base_currency(portfolio, petr4, aapl, trade):
    trade(petr4, "BUY", "2024-01-10", 100, 20)
    trade(aapl, "BUY", "2024-01-10", 10, 150)
    PriceQuote.objects.create(asset=petr4, day="2024-06-03", close=Decimal("30"))
    PriceQuote.objects.create(asset=aapl, day="2024-06-03", close=Decimal("200"))
    FxRate.objects.create(base="USD", quote="BRL", day="2024-06-03", rate=Decimal("5"))

    result = snapshot([portfolio])

    assert result.total_value == Decimal("13000")  # 3000 + 2000 * 5
    assert result.total_cost == Decimal("9500")  # 2000 + 1500 * 5
    assert result.unrealized_gain == Decimal("3500")
    assert [row.asset.ticker for row in result.rows] == ["AAPL", "PETR4"]
    assert result.rows[0].gain == Decimal("500")  # in USD
    assert {s.label: s.value for s in result.by_currency} == {
        "USD": Decimal("10000"),
        "BRL": Decimal("3000"),
    }
    assert sum(row.weight for row in result.rows) == Decimal("100")
    assert not result.unpriced and not result.missing_fx


def test_snapshot_reports_missing_prices_and_rates(portfolio, petr4, aapl, trade):
    trade(petr4, "BUY", "2024-01-10", 100, 20)
    trade(aapl, "BUY", "2024-01-10", 10, 150)

    result = snapshot([portfolio])

    assert result.unpriced == ["AAPL", "PETR4"] or sorted(result.unpriced) == ["AAPL", "PETR4"]
    assert result.missing_fx == ["USD"]
    assert result.total_value == Decimal("2000")  # PETR4 at cost; AAPL left out without a rate
    assert all(row.gain is None for row in result.rows)
