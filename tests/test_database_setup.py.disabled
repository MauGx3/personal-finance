import os
import tempfile
from datetime import datetime

from personal_finance.database import DatabaseManager


def test_sqlite_fallback_creation():
    # Ensure DATABASE_URL not set for fallback
    os.environ.pop('DATABASE_URL', None)
    # Use temp directory for sqlite file isolation
    with tempfile.TemporaryDirectory() as td:
        db_path = os.path.join(td, 'pf.db')
        url = f'sqlite:///{db_path}'
        db = DatabaseManager(database_url=url)
        db.create_tables()
        # Basic insert
        db.add_or_update_ticker('AAPL', 'Apple Inc.', 123.45)
        t = db.get_ticker('AAPL')
        assert t is not None
        assert t.symbol == 'AAPL'


def test_portfolio_and_historical_price_roundtrip():
    with tempfile.TemporaryDirectory() as td:
        url = f"sqlite:///{os.path.join(td, 'pf.db')}"
        db = DatabaseManager(database_url=url)
        db.create_tables()

        # Add position
        db.add_portfolio_position('MSFT', 'Microsoft', 2, 300.0, datetime(2024, 1, 1))
        pos = db.get_portfolio_position('MSFT')
        assert pos is not None
        assert pos.symbol == 'MSFT'

        # Add historical price
        db.add_historical_price('MSFT', datetime(2024, 1, 2), close_price=310.0)
        prices = db.get_historical_prices('MSFT')
        assert len(prices) == 1
        assert prices[0].close_price == 310.0
