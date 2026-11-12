from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.utils import timezone

from apps.assets.models import Asset
from apps.data_sources.models import FxRate, PriceQuote
from apps.data_sources.registry import get_provider
from apps.data_sources.services import fx_rate, latest_quotes, sync_all, sync_asset
from tests.fakes import FakeProvider

pytestmark = pytest.mark.django_db


def test_registry_returns_configured_provider_and_rejects_unknown():
    assert isinstance(get_provider(), FakeProvider)
    with pytest.raises(ImproperlyConfigured):
        get_provider("nope")


def test_sync_asset_is_incremental_and_idempotent(petr4):
    start = timezone.localdate() - timedelta(days=13)
    stored = sync_asset(petr4, FakeProvider(), start)
    assert stored == PriceQuote.objects.count() == 10  # two weeks of weekdays

    sync_asset(petr4, FakeProvider())  # resumes from the last stored day
    assert PriceQuote.objects.count() == 10
    assert latest_quotes([petr4.pk])[petr4.pk].close == Decimal("30")


def test_sync_all_covers_held_assets_and_their_currencies(portfolio, petr4, aapl, trade):
    Asset.objects.create(ticker="VALE3")  # not held: skipped
    unknown = Asset.objects.create(ticker="XXXX3")
    recent = (timezone.localdate() - timedelta(days=7)).isoformat()
    for asset in (petr4, aapl, unknown):
        trade(asset, "BUY", recent, 1, 1)

    report = sync_all()

    assert set(report.quotes) == {"PETR4", "AAPL"}
    assert set(report.fx) == {"USD/BRL"}
    assert set(report.errors) == {"XXXX3"}
    assert FxRate.objects.filter(base="USD", quote="BRL").exists()


def test_fx_rate_lookup():
    assert fx_rate("BRL", "BRL") == 1
    assert fx_rate("USD", "BRL") is None
    FxRate.objects.create(base="USD", quote="BRL", day=date(2024, 1, 2), rate=Decimal("4"))
    FxRate.objects.create(base="USD", quote="BRL", day=date(2024, 6, 3), rate=Decimal("5"))
    assert fx_rate("USD", "BRL") == Decimal("5")
    assert fx_rate("USD", "BRL", on=date(2024, 3, 1)) == Decimal("4")
    assert fx_rate("USD", "BRL", on=date(2023, 1, 1)) is None
    assert fx_rate("BRL", "USD") == Decimal("0.2")


def test_sync_prices_command(portfolio, petr4, trade, capsys):
    trade(petr4, "BUY", (timezone.localdate() - timedelta(days=3)).isoformat(), 1, 1)
    call_command("sync_prices", "--days", "5")
    assert "PETR4" in capsys.readouterr().out
    assert PriceQuote.objects.filter(asset=petr4).exists()
