"""Assets subpackage: modules that gather data from financial assets.

This package houses connectors to external data sources (yfinance,
stockdex, etc.)."""

from . import (
    stockdex,
    yahoo_finance,
)

__all__ = ["stockdex", "yahoo_finance"]
