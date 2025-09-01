"""Database module (PostgreSQL + Alembic only).

Simplified for production use:
 - Requires a PostgreSQL `DATABASE_URL` environment variable (no SQLite fallback).
 - Alembic manages schema; `create_tables` retained only for emergency bootstrap in dev.
 - Legacy JSON migration logic removed (use proper data migrations instead).
"""

import os
import logging
from contextlib import contextmanager
from typing import Optional, List, Generator
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    UniqueConstraint,
    Index,
)

from sqlalchemy.orm import sessionmaker, Session, declarative_base, Mapped, mapped_column
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

# Database models
Base = declarative_base()


class Ticker(Base):
    """Model for stock ticker information"""

    __tablename__ = 'tickers'

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):  # pragma: no cover - simple repr
        return f"<Ticker(symbol='{self.symbol}', name='{self.name}', price={self.price})>"


class PortfolioPosition(Base):
    """Model for portfolio positions.

    One row per symbol (aggregate position). Lots are not individually tracked yet.
    """

    __tablename__ = 'portfolio_positions'

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    buy_price: Mapped[float] = mapped_column(Float, nullable=False)
    buy_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    current_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Data integrity: enforce single row per symbol (matches update logic)
    __table_args__ = (
        UniqueConstraint('symbol', name='uq_portfolio_positions_symbol'),
    )

    def __repr__(self):  # pragma: no cover - simple repr
        return (
            f"<PortfolioPosition(symbol='{self.symbol}', quantity={self.quantity}, "
            f"buy_price={self.buy_price})>"
        )


class HistoricalPrice(Base):
    """Model for historical price data."""

    __tablename__ = 'historical_prices'

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    open_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    high_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    low_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    close_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    volume: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('symbol', 'date', name='uq_historical_prices_symbol_date'),
        Index('ix_historical_prices_symbol_date', 'symbol', 'date'),
    )

    def __repr__(self):  # pragma: no cover - simple repr
        return (
            f"<HistoricalPrice(symbol='{self.symbol}', date='{self.date}', "
            f"close={self.close_price})>"
        )


def _ensure_postgres_url(url: str) -> None:
    if not url.startswith("postgresql://") and not url.startswith("postgresql+"):
        raise ValueError(
            "DATABASE_URL must be a PostgreSQL connection string (postgresql://...)."
        )


class DatabaseManager:
    """Manager class for database operations and migrations."""

    def __init__(self, database_url: Optional[str] = None, echo: bool = False):
        if database_url is None:
            database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise RuntimeError(
                "DATABASE_URL is required (PostgreSQL). Set it in the environment or .env file."
            )
        _ensure_postgres_url(database_url)
        self.database_url = database_url
        self.engine = create_engine(database_url, echo=echo, future=True)
        # Use default expire_on_commit behavior for production safety
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine, future=True)

    def run_migrations(self, revision: str = 'head') -> None:
        """Run Alembic migrations up to the specified revision (default head).

        This allows programmatic control instead of relying on the CLI.
        """
        try:
            try:
                from alembic import command  # type: ignore
                from alembic.config import Config  # type: ignore
            except ImportError as ie:  # pragma: no cover - environment dependent
                raise RuntimeError(
                    "Alembic is not installed. Install with 'pip install alembic' or '\n"
                    "install project with dev extras: 'pip install .[dev]' to run migrations."
                ) from ie

            alembic_cfg = Config(os.path.join(os.path.dirname(__file__), '..', '..', 'alembic.ini'))
            # Ensure consistent path resolution
            script_location = os.path.join(os.path.dirname(__file__), '..', '..', 'alembic')
            alembic_cfg.set_main_option('script_location', os.path.abspath(script_location))
            # Override URL dynamically
            alembic_cfg.set_main_option('sqlalchemy.url', self.database_url)

            command.upgrade(alembic_cfg, revision)
            logger.info("Migrations applied up to revision %s", revision)
        except Exception as exc:
            logger.error("Failed to run migrations: %s", exc)
            raise

    def create_tables(self):  # pragma: no cover - dev convenience only
        """DEV ONLY: Create tables directly (prefer Alembic migrations)."""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Tables created (bypassing Alembic) - for DEV only.")

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Provide a SQLAlchemy session with commit/rollback and cleanup.

        Usage:
            with db.get_session() as session:
                ...
        """
        session: Session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # Ticker operations
    def add_or_update_ticker(self, symbol: str, name: str, price: Optional[float] = None) -> Ticker:
        """Add or update a ticker"""
        with self.get_session() as session:
            ticker = session.query(Ticker).filter(Ticker.symbol == symbol).first()
            if ticker:
                ticker.name = name
                if price is not None:
                    ticker.price = price
                ticker.last_updated = datetime.utcnow()
            else:
                ticker = Ticker(symbol=symbol, name=name, price=price)
                session.add(ticker)
            session.commit()
            return ticker

    def get_ticker(self, symbol: str) -> Optional[Ticker]:
        """Get ticker by symbol"""
        with self.get_session() as session:
            return session.query(Ticker).filter(Ticker.symbol == symbol).first()

    def get_all_tickers(self) -> List[Ticker]:
        """Get all tickers"""
        with self.get_session() as session:
            return session.query(Ticker).all()

    # Portfolio operations
    def add_portfolio_position(self, symbol: str, name: str, quantity: float,
                             buy_price: float, buy_date: datetime) -> PortfolioPosition:
        """Add a portfolio position"""
        with self.get_session() as session:
            position = PortfolioPosition(
                symbol=symbol,
                name=name,
                quantity=quantity,
                buy_price=buy_price,
                buy_date=buy_date
            )
            session.add(position)
            session.commit()
            return position

    def update_portfolio_position(self, symbol: str, quantity: float,
                                buy_price: float, buy_date: datetime) -> Optional[PortfolioPosition]:
        """Update an existing portfolio position"""
        with self.get_session() as session:
            position = session.query(PortfolioPosition).filter(
                PortfolioPosition.symbol == symbol
            ).first()
            if position:
                position.quantity = quantity
                position.buy_price = buy_price
                position.buy_date = buy_date
                position.last_updated = datetime.utcnow()
                session.commit()
            return position

    def get_portfolio_positions(self) -> List[PortfolioPosition]:
        """Get all portfolio positions"""
        with self.get_session() as session:
            return session.query(PortfolioPosition).all()

    def get_portfolio_position(self, symbol: str) -> Optional[PortfolioPosition]:
        """Get portfolio position by symbol"""
        with self.get_session() as session:
            return session.query(PortfolioPosition).filter(
                PortfolioPosition.symbol == symbol
            ).first()

    def remove_portfolio_position(self, symbol: str) -> bool:
        """Remove a portfolio position"""
        with self.get_session() as session:
            position = session.query(PortfolioPosition).filter(
                PortfolioPosition.symbol == symbol
            ).first()
            if position:
                session.delete(position)
                session.commit()
                return True
            return False

    # Historical data operations
    def add_historical_price(self, symbol: str, date: datetime, open_price: Optional[float] = None,
                           high_price: Optional[float] = None, low_price: Optional[float] = None,
                           close_price: Optional[float] = None, volume: Optional[int] = None) -> HistoricalPrice:
        """Add historical price data"""
        with self.get_session() as session:
            # Check if entry already exists
            existing = session.query(HistoricalPrice).filter(
                HistoricalPrice.symbol == symbol,
                HistoricalPrice.date == date
            ).first()

            if existing:
                # Update existing entry
                if open_price is not None:
                    existing.open_price = open_price
                if high_price is not None:
                    existing.high_price = high_price
                if low_price is not None:
                    existing.low_price = low_price
                if close_price is not None:
                    existing.close_price = close_price
                if volume is not None:
                    existing.volume = volume
                existing.last_updated = datetime.utcnow()
                price_entry = existing
            else:
                # Create new entry
                price_entry = HistoricalPrice(
                    symbol=symbol,
                    date=date,
                    open_price=open_price,
                    high_price=high_price,
                    low_price=low_price,
                    close_price=close_price,
                    volume=volume
                )
                session.add(price_entry)

            session.commit()
            return price_entry

    def get_historical_prices(self, symbol: str, start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None) -> List[HistoricalPrice]:
        """Get historical prices for a symbol"""
        with self.get_session() as session:
            query = session.query(HistoricalPrice).filter(HistoricalPrice.symbol == symbol)

            if start_date:
                query = query.filter(HistoricalPrice.date >= start_date)
            if end_date:
                query = query.filter(HistoricalPrice.date <= end_date)

            return query.order_by(HistoricalPrice.date).all()

    # (Legacy JSON migration removed – use dedicated Alembic data migrations instead.)
