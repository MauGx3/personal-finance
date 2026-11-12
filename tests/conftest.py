import secrets
from datetime import date
from decimal import Decimal

import pytest

from apps.assets.models import Asset, Exchange
from apps.portfolios.models import Portfolio, Transaction
from apps.users.models import User

# Generated per run, so no credential is written in the repository.
TEST_PASSWORD = secrets.token_urlsafe(12)


@pytest.fixture
def user():
    return User.objects.create_user(email="me@example.com", password=TEST_PASSWORD)


@pytest.fixture
def other_user():
    return User.objects.create_user(email="other@example.com", password=TEST_PASSWORD)


@pytest.fixture
def portfolio(user):
    return Portfolio.objects.create(user=user, name="Main")


@pytest.fixture
def petr4():
    return Asset.objects.create(ticker="PETR4", exchange=Exchange.B3, currency="BRL")


@pytest.fixture
def aapl():
    return Asset.objects.create(ticker="AAPL", exchange=Exchange.NASDAQ, currency="USD")


@pytest.fixture
def trade(portfolio):
    """Factory for transactions: ``trade(asset, "BUY", "2024-01-10", 100, "25.50")``."""

    def make(asset, kind, day, quantity=0, price=0, fees=0, amount=0, **extra):
        return Transaction.objects.create(
            portfolio=extra.pop("portfolio", portfolio),
            asset=asset,
            kind=kind,
            trade_date=date.fromisoformat(day),
            quantity=Decimal(str(quantity)),
            price=Decimal(str(price)),
            fees=Decimal(str(fees)),
            amount=Decimal(str(amount)),
            **extra,
        )

    return make
