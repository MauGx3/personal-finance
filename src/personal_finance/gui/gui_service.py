"""Simple service adapter used by GUI frontends.

This lives on top of DatabaseManager and exposes a small, stable API
that both a web frontend and a local desktop GUI can call.

Pass an explicit database_url to use a local DB for development (e.g. sqlite)
or omit to use environment `DATABASE_URL` (production).
"""
from typing import List, Optional
from datetime import datetime

from ..database import DatabaseManager, Ticker, PortfolioPosition, HistoricalPrice


class GUIService:
    def __init__(self, database_url: Optional[str] = None, echo: bool = False):
        """Create service.

        If database_url is provided, it will be passed to DatabaseManager
        (useful for local dev with sqlite). In production omit it and
        let DatabaseManager use the required DATABASE_URL env var.
        """
        self.db = DatabaseManager(database_url=database_url, echo=echo)

    # Tickers
    def list_tickers(self) -> List[Ticker]:
        return self.db.get_all_tickers()

    def get_ticker(self, symbol: str) -> Optional[Ticker]:
        return self.db.get_ticker(symbol)

    def add_ticker(self, symbol: str, name: str, price: Optional[float] = None) -> Ticker:
        return self.db.add_or_update_ticker(symbol, name, price)

    # Portfolio
    def list_positions(self) -> List[PortfolioPosition]:
        return self.db.get_portfolio_positions()

    def add_position(self, symbol: str, name: str, quantity: float, buy_price: float, buy_date: datetime) -> PortfolioPosition:
        return self.db.add_portfolio_position(symbol, name, quantity, buy_price, buy_date)

    def update_position(self, symbol: str, quantity: float, buy_price: float, buy_date: datetime) -> Optional[PortfolioPosition]:
        return self.db.update_portfolio_position(symbol, quantity, buy_price, buy_date)

    def remove_position(self, symbol: str) -> bool:
        return self.db.remove_portfolio_position(symbol)

    # Historical prices
    def add_price(self, symbol: str, date: datetime, open_price: Optional[float] = None,
                  high_price: Optional[float] = None, low_price: Optional[float] = None,
                  close_price: Optional[float] = None, volume: Optional[int] = None) -> HistoricalPrice:
        return self.db.add_historical_price(symbol, date, open_price, high_price, low_price, close_price, volume)

    def list_prices(self, symbol: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[HistoricalPrice]:
        return self.db.get_historical_prices(symbol, start_date, end_date)
