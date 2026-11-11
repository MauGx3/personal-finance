"""The contract every market data provider implements.

Deliberately small: the app needs daily closes (for assets and for currency
pairs) and, optionally, a few descriptive fields. A new provider is a class
with these methods, registered in ``settings.PRICE_PROVIDERS``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


class ProviderError(Exception):
    """The provider could not answer (network, rate limit, bad payload)."""


class SymbolNotFound(ProviderError):
    """The provider does not know this symbol."""


@dataclass(frozen=True)
class DailyClose:
    day: date
    close: Decimal


@dataclass(frozen=True)
class SymbolInfo:
    name: str = ""
    currency: str = ""
    sector: str = ""
    quote_type: str = ""


class PriceProvider(ABC):
    name: str = ""

    @abstractmethod
    def daily_closes(self, symbol: str, start: date, end: date) -> list[DailyClose]:
        """Return closes for ``start <= day <= end``, oldest first."""

    def fx_symbol(self, base: str, quote: str) -> str:
        """Symbol for the price of one ``base`` in ``quote`` (Yahoo convention)."""
        return f"{base}{quote}=X"

    def info(self, symbol: str) -> SymbolInfo:
        """Descriptive data for a symbol. Optional; empty by default."""
        return SymbolInfo()
