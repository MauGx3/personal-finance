"""Yahoo Finance provider, through the ``yfinance`` package."""

from __future__ import annotations

import logging
from datetime import date, timedelta

from apps.core.money import to_decimal

from ..base import DailyClose, PriceProvider, ProviderError, SymbolInfo, SymbolNotFound

logger = logging.getLogger(__name__)


class YFinanceProvider(PriceProvider):
    name = "yfinance"

    def daily_closes(self, symbol: str, start: date, end: date) -> list[DailyClose]:
        import yfinance as yf  # imported lazily: it pulls in pandas

        try:
            frame = yf.Ticker(symbol).history(
                start=start.isoformat(),
                end=(end + timedelta(days=1)).isoformat(),  # yfinance's end is exclusive
                interval="1d",
                auto_adjust=False,
            )
        except Exception as exc:  # yfinance raises a wide range of errors
            raise ProviderError(f"yfinance failed for {symbol}: {exc}") from exc

        if frame is None or frame.empty or "Close" not in frame:
            raise SymbolNotFound(f"No price data for {symbol} between {start} and {end}.")

        closes = []
        for timestamp, value in frame["Close"].dropna().items():
            try:
                closes.append(DailyClose(timestamp.date(), to_decimal(repr(float(value)))))
            except ValueError:
                logger.warning("Skipping unreadable close for %s on %s", symbol, timestamp)
        return closes

    def info(self, symbol: str) -> SymbolInfo:
        import yfinance as yf

        try:
            data = yf.Ticker(symbol).info or {}
        except Exception as exc:
            raise ProviderError(f"yfinance failed for {symbol}: {exc}") from exc
        return SymbolInfo(
            name=data.get("longName") or data.get("shortName") or "",
            currency=(data.get("currency") or "").upper(),
            sector=data.get("sector") or "",
            quote_type=data.get("quoteType") or "",
        )
