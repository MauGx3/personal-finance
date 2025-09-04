"""Compatibility wrapper around the external `stockdex` package.

This module provides a lightweight `get_last_close` helper that avoids
performing network calls at import time (the previous implementation
called `get_last_close` and printed a value during import). Tests and
applications can continue to import `personal_finance._stockdex` or
`personal_finance.stockdex` (there is a shim) and call `get_last_close`.
"""

from typing import Optional

try:
    from stockdex import Ticker  # external package
except Exception:  # pragma: no cover - runtime environment may not have stockdex
    Ticker = None


def get_last_close(symbol: str) -> Optional[float]:
    """Return the last close price for `symbol` using stockdex if available.

    Returns None if the `stockdex` package is not installed or if the
    underlying call fails.
    """
    if Ticker is None:
        return None

    try:
        t = Ticker(symbol)
        # The stockdex Ticker exposes a method to fetch prices; keep this
        # defensive to avoid raising on unexpected library changes.
        series = t.yahoo_api_price(range="1d", dataGranularity="1d").get("close")
        if series is None or len(series) == 0:
            return None
        return float(series.iloc[-1])
    except Exception:
        return None
