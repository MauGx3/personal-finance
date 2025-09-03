"""Database module.

Supports SQL backends and MongoDB. Alembic is used for SQL migrations.
"""

import os
import logging
from contextlib import contextmanager
from typing import Optional, List, Generator, Any
from sqlalchemy import (
    create_engine,
    text,
    Integer,
    String,
    Float,
    DateTime,
    UniqueConstraint,
    Index,
)

from sqlalchemy.orm import (
    sessionmaker,
    Session,
    declarative_base,
    Mapped,
    mapped_column,
)
from datetime import datetime, timezone
from types import SimpleNamespace

# Configure logging
logger = logging.getLogger(__name__)

# Database models
Base = declarative_base()


class Ticker(Base):
    """Model for stock ticker information"""

    __tablename__ = 'tickers'

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(
        String(10), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):  # pragma: no cover - simple repr
        return (
            f"<Ticker(symbol='{self.symbol}', name='{self.name}', "
            f"price={self.price})>"
        )


class PortfolioPosition(Base):
    """Model for portfolio positions.

    One row per symbol (aggregate position).
    Lots are not individually tracked yet.
    """

    __tablename__ = 'portfolio_positions'

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(
        String(10), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    buy_price: Mapped[float] = mapped_column(Float, nullable=False)
    buy_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    current_price: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Data integrity: enforce single row per symbol (matches update logic)
    __table_args__ = (
        UniqueConstraint('symbol', name='uq_portfolio_positions_symbol'),
    )

    def __repr__(self):  # pragma: no cover - simple repr
        return (
            f"<PortfolioPosition(symbol='{self.symbol}', "
            f"quantity={self.quantity}, buy_price={self.buy_price})>"
        )


class HistoricalPrice(Base):
    """Model for historical price data."""

    __tablename__ = 'historical_prices'

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(
        String(10), nullable=False, index=True
    )
    date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True
    )
    open_price: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    high_price: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    low_price: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    close_price: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    volume: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        UniqueConstraint(
            'symbol', 'date', name='uq_historical_prices_symbol_date'
        ),
        Index('ix_historical_prices_symbol_date', 'symbol', 'date'),
    )

    def __repr__(self):  # pragma: no cover - simple repr
        return (
            f"<HistoricalPrice(symbol='{self.symbol}', date='{self.date}', "
            f"close={self.close_price})>"
        )


def _ensure_postgres_url(url: str) -> None:
    if not (
        url.startswith("postgresql://")
        or url.startswith("postgresql+")
        or url.startswith("sqlite:///")
    ):
        raise ValueError(
            "DATABASE_URL must be a PostgreSQL connection string "
            "(postgresql://...) or SQLite (sqlite:///) for testing."
        )


class DatabaseManager:
    """Manager class for database operations and migrations."""
    def __init__(self, database_url: Optional[str] = None, echo: bool = False):
        if database_url is None:
            database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise RuntimeError(
                "DATABASE_URL is required (Postgres, SQLite for testing, or "
                "MongoDB). Set it in the environment or .env file."
            )
        self.database_url = database_url
        # Detect backend by scheme
        if (
            database_url.startswith("mongodb://")
            or database_url.startswith("mongodb+srv://")
        ):
            # MongoDB backend
            self.backend = 'mongodb'
            try:
                from pymongo import MongoClient  # type: ignore
            except Exception as ie:  # pragma: no cover - environment dependent
                raise RuntimeError(
                    "pymongo is required for MongoDB support. "
                    "Install with 'pip install pymongo'"
                ) from ie
            # Lazily create client and DB
            self._mongo_client = MongoClient(database_url)
            # If a DB name is present in the URL, use it; otherwise default to
            # 'personal_finance'. PyMongo parses the DB from the URI path.
            parsed = database_url.split('/')
            dbname = parsed[-1] or 'personal_finance'
            self.mongo_db = self._mongo_client[dbname]
            self._mongo_collections = {
                'tickers': self.mongo_db['tickers'],
                'portfolio_positions': self.mongo_db['portfolio_positions'],
                'historical_prices': self.mongo_db['historical_prices'],
            }
            self.engine = None
            self.SessionLocal = None
        else:
            # Default: SQL (Postgres/SQLite)
            _ensure_postgres_url(database_url)
            self.backend = 'sql'
            self.engine = create_engine(database_url, echo=echo, future=True)
            # Use default expire_on_commit behavior for production safety
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine,
                future=True,
                expire_on_commit=False,
            )
            self._mongo_client = None

    def run_migrations(self, revision: str = 'head') -> None:
        """Run Alembic migrations up to the specified revision (default head).

        This allows programmatic control instead of relying on the CLI.
        """
        try:
            try:
                from alembic import command  # type: ignore
                from alembic.config import Config  # type: ignore
            except ImportError as ie:  # pragma: no cover
                raise RuntimeError(
                    "Alembic is not installed. Install with 'pip install alembic' "
                    "or install project with dev extras: 'pip install .[dev]'"
                ) from ie

            # Candidate locations to search for alembic scripts (ordered)
            candidates = []
            pkg_dir = os.path.dirname(os.path.abspath(__file__))
            source_layout = os.path.abspath(os.path.join(pkg_dir, '..', '..'))
            candidates.append(source_layout)
            candidates.append(os.getenv('APP_ROOT', '/app'))
            candidates.append(os.getcwd())

            script_location = None
            ini_path = None
            for root in candidates:
                if not root:
                    continue
                cand_script = os.path.join(root, 'alembic')
                cand_ini = os.path.join(root, 'alembic.ini')
                if os.path.isdir(cand_script) and os.path.isfile(cand_ini):
                    script_location = cand_script
                    ini_path = cand_ini
                    break

            if not script_location or not ini_path:
                msg = (
                    "Alembic scripts directory not found in searched locations: "
                    + ", ".join(candidates)
                )
                raise RuntimeError(msg)

            if self.backend == 'mongodb':
                # MongoDB: skip Alembic migrations
                logger.info(
                    "Skipping Alembic migrations for MongoDB backend"
                )
                return

            alembic_cfg = Config(ini_path)
            script_abs = os.path.abspath(script_location)
            alembic_cfg.set_main_option('script_location', script_abs)
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
    def get_session(self) -> Generator[Any, None, None]:
        """Provide a SQLAlchemy session with commit/rollback and cleanup.

        Usage:
            with db.get_session() as session:
                ...
        This yields a real SQLAlchemy Session for SQL backends and a small
        dummy session object for MongoDB so existing code using the
        contextmanager continues to work.
        """
        # Provide a compatible context manager for both SQL and MongoDB.
        if self.backend == 'sql':
            assert self.SessionLocal is not None
            session: Session = self.SessionLocal()
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()
        else:
            # For MongoDB yield a dummy session object. Methods use mongo
            # collections directly.
            class _DummySession:
                def execute(self, *_a, **_k):
                    return None

            yield _DummySession()

    # Ticker operations
    def add_or_update_ticker(
        self, symbol: str, name: str, price: Optional[float] = None
    ) -> Any:
        """Add or update a ticker."""
        if self.backend == 'sql':
            with self.get_session() as session:
                ticker = (
                    session.query(Ticker)
                    .filter(Ticker.symbol == symbol)
                    .first()
                )
                if ticker:
                    ticker.name = name
                    if price is not None:
                        ticker.price = price
                        ticker.last_updated = datetime.now(timezone.utc)
                else:
                    ticker = Ticker(symbol=symbol, name=name, price=price)
                    session.add(ticker)
                session.commit()
                # Ensure the instance is refreshed from DB so attributes are
                # available after the session is closed (prevents detached
                # instance issues when callers access attributes).
                try:
                    session.refresh(ticker)
                except Exception:
                    # If refresh fails for any reason, fall back to returning
                    # the instance as-is; callers should handle attribute
                    # access defensively.
                    pass
                return ticker
        else:
            # MongoDB upsert
            doc = {
                'symbol': symbol,
                'name': name,
                'price': price,
                'last_updated': datetime.now(timezone.utc),
            }
            res = self._mongo_collections['tickers'].find_one_and_update(
                {'symbol': symbol},
                {'$set': doc},
                upsert=True,
                return_document=True,
            )
            # convert to simple object
            return SimpleNamespace(**(res or doc))

    def get_ticker(self, symbol: str) -> Optional[Any]:
        """Get ticker by symbol."""
        if self.backend == 'sql':
            with self.get_session() as session:
                return (
                    session.query(Ticker)
                    .filter(Ticker.symbol == symbol)
                    .first()
                )
        else:
            doc = self._mongo_collections['tickers'].find_one(
                {'symbol': symbol}
            )
            return SimpleNamespace(**doc) if doc else None

    def get_all_tickers(self) -> List[Any]:
        """Get all tickers"""
        if self.backend == 'sql':
            with self.get_session() as session:
                return session.query(Ticker).all()
        else:
            coll = self._mongo_collections['tickers']
            docs = list(coll.find())
            return [SimpleNamespace(**d) for d in docs]

    # Portfolio operations
    def add_portfolio_position(
        self,
        symbol: str,
        name: str,
        quantity: float,
        buy_price: float,
        buy_date: datetime,
    ) -> Any:
        """Add a portfolio position."""
        if self.backend == 'sql':
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
                try:
                    session.refresh(position)
                except Exception:
                    pass
                return position
        else:
            doc = {
                'symbol': symbol,
                'name': name,
                'quantity': quantity,
                'buy_price': buy_price,
                'buy_date': buy_date,
                'current_price': None,
                'last_updated': datetime.now(timezone.utc),
            }
            self._mongo_collections['portfolio_positions'].insert_one(doc)
            return SimpleNamespace(**doc)

    def update_portfolio_position(
        self,
        symbol: str,
        quantity: float,
        buy_price: float,
        buy_date: datetime,
    ) -> Optional[Any]:
        """Update an existing portfolio position."""
        if self.backend == 'sql':
            with self.get_session() as session:
                position = session.query(PortfolioPosition).filter(
                    PortfolioPosition.symbol == symbol
                ).first()
                if position:
                    position.quantity = quantity
                    position.buy_price = buy_price
                    position.buy_date = buy_date
                    position.last_updated = datetime.now(timezone.utc)
                    session.commit()
                    try:
                        session.refresh(position)
                    except Exception:
                        pass
                return position
        else:
            res = self._mongo_collections['portfolio_positions'].find_one_and_update(
                {'symbol': symbol},
                {
                    '$set': {
                        'quantity': quantity,
                        'buy_price': buy_price,
                        'buy_date': buy_date,
                        'last_updated': datetime.now(timezone.utc),
                    }
                },
                return_document=True,
            )
            return SimpleNamespace(**res) if res else None

    def get_portfolio_positions(self) -> List[Any]:
        """Get all portfolio positions"""
        if self.backend == 'sql':
            with self.get_session() as session:
                return session.query(PortfolioPosition).all()
        else:
            coll = self._mongo_collections['portfolio_positions']
            docs = list(coll.find())
            return [SimpleNamespace(**d) for d in docs]

    def get_portfolio_position(
        self, symbol: str
    ) -> Optional[Any]:
        """Get portfolio position by symbol"""
        if self.backend == 'sql':
            with self.get_session() as session:
                return session.query(PortfolioPosition).filter(
                    PortfolioPosition.symbol == symbol
                ).first()
        else:
            doc = self._mongo_collections['portfolio_positions'].find_one(
                {'symbol': symbol}
            )
            return SimpleNamespace(**doc) if doc else None

    def remove_portfolio_position(self, symbol: str) -> bool:
        """Remove a portfolio position"""
        if self.backend == 'sql':
            with self.get_session() as session:
                position = session.query(PortfolioPosition).filter(
                    PortfolioPosition.symbol == symbol
                ).first()
                if position:
                    session.delete(position)
                    session.commit()
                    return True
                return False
        else:
            res = self._mongo_collections['portfolio_positions'].delete_one(
                {'symbol': symbol}
            )
            return res.deleted_count > 0

    # Historical data operations
    def add_historical_price(
        self,
        symbol: str,
        date: datetime,
        open_price: Optional[float] = None,
        high_price: Optional[float] = None,
        low_price: Optional[float] = None,
        close_price: Optional[float] = None,
        volume: Optional[int] = None,
    ) -> Any:
        """Add historical price data."""
        if self.backend == 'sql':
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
                    existing.last_updated = datetime.now(timezone.utc)
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
                try:
                    session.refresh(price_entry)
                except Exception:
                    pass
                return price_entry
        else:
            # Upsert by symbol+date
            doc = {
                'symbol': symbol,
                'date': date,
                'open_price': open_price,
                'high_price': high_price,
                'low_price': low_price,
                'close_price': close_price,
                'volume': volume,
                'last_updated': datetime.now(timezone.utc),
            }
            self._mongo_collections['historical_prices'].update_one(
                {'symbol': symbol, 'date': date},
                {'$set': doc},
                upsert=True,
            )
            return SimpleNamespace(**doc)

    def get_historical_prices(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Any]:
        """Get historical prices for a symbol."""
        if self.backend == 'sql':
            with self.get_session() as session:
                query = (
                    session.query(HistoricalPrice)
                    .filter(HistoricalPrice.symbol == symbol)
                )

                if start_date:
                    query = query.filter(HistoricalPrice.date >= start_date)
                if end_date:
                    query = query.filter(HistoricalPrice.date <= end_date)

                return query.order_by(HistoricalPrice.date).all()
        else:
            q = {'symbol': symbol}
            if start_date or end_date:
                date_filter: dict = {}
                if start_date:
                    date_filter['$gte'] = start_date
                if end_date:
                    date_filter['$lte'] = end_date
                q['date'] = date_filter
            coll = self._mongo_collections['historical_prices']
            docs = list(coll.find(q).sort('date', 1))
            return [SimpleNamespace(**d) for d in docs]

    def ping(self) -> bool:
        """Check DB connectivity for both backends."""
        try:
            if self.backend == 'sql':
                with self.get_session() as session:
                    # simple no-op execute compatible with SQLAlchemy session
                    session.execute(text('SELECT 1'))
                return True
            else:
                # pymongo has a ping command
                if self._mongo_client is None:
                    raise RuntimeError("Mongo client not initialized")
                self._mongo_client.admin.command('ping')
                return True
        except Exception as exc:
            logger.warning('DB ping failed: %s', exc)
            return False

    # Legacy JSON migration removed - use Alembic data migrations instead.
