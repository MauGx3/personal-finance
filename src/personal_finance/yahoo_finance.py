"""Backward-compatible shim for personal_finance.yahoo_finance
Re-exports functions from personal_finance.assets.yahoo_finance
"""

from .assets.yahoo_finance import *  # noqa: F401,F403
import yfinance
import logging
import requests
import json
from datetime import datetime
from typing import Optional, Dict, List
from .database import DatabaseManager

logger = logging.getLogger(__name__)


def verify_yfinance():
    """Verify that yfinance is working properly"""
    try:
        ticker = yfinance.Ticker("AAPL")
        data = ticker.history(period="1d")
        if data.empty:
            logging.warning("yfinance returned empty data")
            return False
        return True
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        logging.error("yfinance verification failed: %s", e)
        return False


def get_ticker_price(
    symbol: str, db_manager: Optional[DatabaseManager] = None
) -> float:
    """Helper method to get current price for a single ticker"""
    try:
        ticker = yfinance.Ticker(symbol)
        # Get today's data
        hist = ticker.history(period="1d")
        if not hist.empty:
            price = hist["Close"].iloc[-1]

            # Store in database if manager provided
            if db_manager:
                # Get ticker info
                info = ticker.info
                name = info.get("longName", info.get("shortName", symbol))
                db_manager.add_or_update_ticker(symbol, name, price)

            return price
        logging.warning("No price data available for %s", symbol)
        return 0
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        logging.error("Error fetching price for %s: %s", symbol, e)
        return 0


def fetch_and_store_historical_data(
    symbol: str,
    period: str = "1y",
    db_manager: Optional[DatabaseManager] = None,
) -> Optional[Dict]:
    """Fetch historical data and store in database"""
    try:
        ticker = yfinance.Ticker(symbol)
        hist = ticker.history(period=period)

        if hist.empty:
            logging.warning("No historical data available for %s", symbol)
            return None

        # Store in database if manager provided
        if db_manager:
            # Get ticker info
            info = ticker.info
            name = info.get("longName", info.get("shortName", symbol))
            db_manager.add_or_update_ticker(symbol, name)

            # Store historical data
            for date, row in hist.iterrows():
                db_manager.add_historical_price(
                    symbol=symbol,
                    date=date.to_pydatetime(),
                    open_price=row.get("Open"),
                    high_price=row.get("High"),
                    low_price=row.get("Low"),
                    close_price=row.get("Close"),
                    volume=row.get("Volume"),
                )

        return hist.to_dict()

    except Exception as e:
        logging.error("Error fetching historical data for %s: %s", symbol, e)
        return None


def get_stored_historical_data(
    symbol: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db_manager: Optional[DatabaseManager] = None,
) -> List[Dict]:
    """Get historical data from database"""
    if not db_manager:
        return []

    try:
        prices = db_manager.get_historical_prices(symbol, start_date, end_date)
        return [
            {
                "date": price.date,
                "open": price.open_price,
                "high": price.high_price,
                "low": price.low_price,
                "close": price.close_price,
                "volume": price.volume,
            }
            for price in prices
        ]
    except Exception as e:
        logging.error("Error retrieving historical data for %s: %s", symbol, e)
        return []


def update_all_ticker_prices(db_manager: DatabaseManager):
    """Update prices for all tickers in database"""
    try:
        tickers = db_manager.get_all_tickers()
        updated_count = 0

        for ticker in tickers:
            price = get_ticker_price(ticker.symbol, db_manager)
            if price > 0:
                updated_count += 1

        logging.info(f"Updated prices for {updated_count} tickers")
        return updated_count

    except Exception as e:
        logging.error("Error updating ticker prices: %s", e)
        return 0


if __name__ == "__main__":
    verify_yfinance()
