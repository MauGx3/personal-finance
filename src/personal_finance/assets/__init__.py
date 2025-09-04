"""Assets subpackage: modules that gather data from financial assets.

This package houses connectors to external data sources (yfinance,
stockdex, etc.)."""

from . import yahoo_finance  # noqa: F401
from . import stockdex  # noqa: F401

__all__ = ["yahoo_finance", "stockdex"]
