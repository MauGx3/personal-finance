"""Test doubles."""

from datetime import date, timedelta
from decimal import Decimal

from apps.data_sources.base import DailyClose, PriceProvider, SymbolNotFound


class FakeProvider(PriceProvider):
    """Returns a fixed price per symbol for every weekday in the range."""

    name = "fake"
    prices = {"PETR4.SA": Decimal("30"), "AAPL": Decimal("200"), "USDBRL=X": Decimal("5")}

    def daily_closes(self, symbol: str, start: date, end: date) -> list[DailyClose]:
        if symbol not in self.prices:
            raise SymbolNotFound(f"No price data for {symbol}.")
        days = (start + timedelta(days=n) for n in range((end - start).days + 1))
        return [DailyClose(day, self.prices[symbol]) for day in days if day.weekday() < 5]
