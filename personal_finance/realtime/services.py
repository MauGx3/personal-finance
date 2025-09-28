"""
Real-time price feed service for WebSocket updates.

This module handles live market data streaming, price updates,
and integration with multiple data sources for real-time feeds.
"""

import asyncio
from loguru import logger
from typing import Dict, List, Set, Any, Optional, Callable
from datetime import datetime
from decimal import Decimal
from dataclasses import dataclass

from django.conf import settings
from django.utils import timezone
from django.core.cache import cache

try:
    from personal_finance.assets.models import Asset
    from personal_finance.portfolios.models import Portfolio, Position
except ImportError:
    # Graceful fallback for missing models
    Asset = None
    Portfolio = None
    Position = None


# Temporary stub for PriceHistory; replace with actual model ASAP
class PriceHistory:
    """Stub PriceHistory model. Should be replaced with the real model."""

    @classmethod
    def objects(cls):
        raise NotImplementedError(
            "PriceHistory.objects is a stub. Implement the actual model."
        )


try:
    from personal_finance.data_sources.services import data_source_manager
except ImportError:
    data_source_manager = None

try:
    from personal_finance.realtime.connections import (
        connection_manager,
        encode_message,
    )
except ImportError:
    connection_manager = None

    def encode_message(data):
        return data


# Using loguru logger imported above


@dataclass
class PricePoint:
    """Structured price data for realtime updates."""

    symbol: str
    price: Decimal
    change: Optional[Decimal] = None
    change_percent: Optional[Decimal] = None
    volume: Optional[int] = None
    high: Optional[Decimal] = None
    low: Optional[Decimal] = None
    timestamp: datetime = None
    source: str = "realtime"

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "symbol": self.symbol,
            "price": float(self.price),
            "change": float(self.change) if self.change is not None else None,
            "change_percent": float(self.change_percent)
            if self.change_percent is not None
            else None,
            "volume": self.volume,
            "high": float(self.high) if self.high is not None else None,
            "low": float(self.low) if self.low is not None else None,
            "timestamp": self.timestamp.isoformat()
            if self.timestamp
            else None,
            "source": self.source,
        }


class RealtimeService:
    """
    Realtime price streaming service with polling and websocket support.

    Provides a simple publish/subscribe API for receiving near real-time
    price updates from multiple data sources. Supports both polling mode
    (periodic HTTP queries) and websocket mode (push updates to clients).
    """

    def __init__(
        self,
        mode: str = "polling",
        update_interval: int = 15,
        max_batch_size: int = 50,
    ):
        """
        Initialize the realtime service.

        Args:
            mode: Operating mode - "polling" or "ws" (websocket)
            update_interval: Seconds between price updates (default 15s)
            max_batch_size: Maximum symbols to process in one batch
        """
        self.mode = mode
        self.update_interval = update_interval
        self.max_batch_size = max_batch_size
        self.is_running = False
        self.update_task = None

        # Subscriber management
        self.subscribers: Dict[
            str, List[Callable]
        ] = {}  # symbol -> [callbacks]
        self._subscription_lock = asyncio.Lock()

        # Graceful shutdown support
        self._shutdown_event = asyncio.Event()

    async def start(self):
        """Start the realtime service."""
        if self.is_running:
            logger.warning("RealtimeService is already running")
            return

        self.is_running = True

        if self.mode == "polling":
            self.update_task = asyncio.create_task(self._polling_loop())
        elif self.mode == "ws":
            # Websocket mode relies on external websocket server
            # but we can still run background updates
            self.update_task = asyncio.create_task(self._polling_loop())
        else:
            raise ValueError(
                f"Invalid mode: {self.mode}. Must be 'polling' or 'ws'"
            )

        logger.info(f"RealtimeService started in {self.mode} mode")

    async def stop(self):
        """Stop the realtime service gracefully."""
        logger.info("Stopping RealtimeService...")
        self.is_running = False
        self._shutdown_event.set()

        if self.update_task:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass

        logger.info("RealtimeService stopped")

    async def subscribe(self, symbols: List[str], callback: Callable):
        """
        Subscribe to price updates for given symbols.

        Args:
            symbols: List of asset symbols to subscribe to
            callback: Function to call with PricePoint objects
        """
        async with self._subscription_lock:
            for symbol in symbols:
                if symbol not in self.subscribers:
                    self.subscribers[symbol] = []
                self.subscribers[symbol].append(callback)

        logger.info(f"Subscribed to {len(symbols)} symbols: {symbols}")

    async def unsubscribe(self, symbols: List[str], callback: Callable):
        """
        Unsubscribe from price updates.

        Args:
            symbols: List of asset symbols to unsubscribe from
            callback: Callback function to remove
        """
        async with self._subscription_lock:
            for symbol in symbols:
                if (
                    symbol in self.subscribers
                    and callback in self.subscribers[symbol]
                ):
                    self.subscribers[symbol].remove(callback)
                    if not self.subscribers[
                        symbol
                    ]:  # Remove empty subscriber list
                        del self.subscribers[symbol]

        logger.info(f"Unsubscribed from {len(symbols)} symbols: {symbols}")

    async def get_subscribed_symbols(self) -> List[str]:
        """Get list of currently subscribed symbols."""
        async with self._subscription_lock:
            return list(self.subscribers.keys())

    async def _polling_loop(self):
        """Main polling loop for price updates."""
        while self.is_running:
            try:
                await self._update_subscribed_prices()
                await asyncio.sleep(self.update_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                await asyncio.sleep(self.update_interval)

    async def _update_subscribed_prices(self):
        """Update prices for all subscribed symbols."""
        symbols = await self.get_subscribed_symbols()
        if not symbols:
            return

        logger.debug(f"Updating prices for {len(symbols)} subscribed symbols")

        # Process in batches to respect rate limits
        for i in range(0, len(symbols), self.max_batch_size):
            batch = symbols[i : i + self.max_batch_size]
            await self._update_batch(batch)

    async def _update_batch(self, symbols: List[str]):
        """Update prices for a batch of symbols."""
        try:
            price_updates = await self._fetch_prices(symbols)

            # Notify subscribers
            for symbol, price_data in price_updates.items():
                await self._notify_subscribers(symbol, price_data)

        except Exception as e:
            logger.error(f"Error updating batch {symbols}: {e}")

    async def _fetch_prices(self, symbols: List[str]) -> Dict[str, PricePoint]:
        """Fetch current prices from data source manager."""
        price_updates = {}

        # Use data_source_manager if available
        if data_source_manager is None:
            logger.warning(
                "data_source_manager not available, using mock data"
            )
            return self._generate_mock_prices(symbols)

        for symbol in symbols:
            try:
                price_data = data_source_manager.get_current_price(symbol)
                if price_data:
                    price_point = PricePoint(
                        symbol=symbol,
                        price=price_data.current_price,
                        change=price_data.current_price
                        - price_data.previous_close
                        if price_data.previous_close
                        else None,
                        change_percent=(
                            (
                                (
                                    price_data.current_price
                                    - price_data.previous_close
                                )
                                / price_data.previous_close
                            )
                            * 100
                            if price_data.previous_close
                            and price_data.previous_close != 0
                            else None
                        ),
                        volume=price_data.volume,
                        high=price_data.day_high,
                        low=price_data.day_low,
                        timestamp=price_data.last_updated,
                        source=getattr(price_data, "source", "data_source"),
                    )
                    price_updates[symbol] = price_point

            except Exception as e:
                logger.error(f"Error fetching price for {symbol}: {e}")

        return price_updates

    def _generate_mock_prices(
        self, symbols: List[str]
    ) -> Dict[str, PricePoint]:
        """Generate mock price data for testing purposes."""
        import random

        price_updates = {}

        for symbol in symbols:
            base_price = 100 + random.uniform(
                -50, 150
            )  # Random price between 50-250
            change = random.uniform(-5, 5)
            change_percent = (change / base_price) * 100

            price_point = PricePoint(
                symbol=symbol,
                price=Decimal(str(round(base_price + change, 2))),
                change=Decimal(str(round(change, 2))),
                change_percent=Decimal(str(round(change_percent, 2))),
                volume=random.randint(1000, 1000000),
                high=Decimal(
                    str(
                        round(
                            base_price + abs(change) + random.uniform(0, 3), 2
                        )
                    )
                ),
                low=Decimal(
                    str(round(base_price + change - random.uniform(0, 3), 2))
                ),
                source="mock",
            )
            price_updates[symbol] = price_point

        return price_updates

    async def _notify_subscribers(self, symbol: str, price_point: PricePoint):
        """Notify all subscribers for a symbol with new price data."""
        async with self._subscription_lock:
            callbacks = self.subscribers.get(symbol, [])

        if not callbacks:
            return

        logger.debug(f"Notifying {len(callbacks)} subscribers for {symbol}")

        # Call all callbacks for this symbol
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(price_point)
                else:
                    callback(price_point)
            except Exception as e:
                logger.error(
                    f"Error calling subscriber callback for {symbol}: {e}"
                )


# Global realtime service instance
realtime_service = RealtimeService()


class PriceFeedService:
    """
    Real-time price feed service for live market data updates.

    Manages price streaming from multiple data sources and broadcasts
    updates to subscribed WebSocket connections.
    """

    def __init__(self):
        """Initialize the price feed service."""
        self.update_interval = getattr(
            settings, "REALTIME_UPDATE_INTERVAL", 30
        )  # seconds
        self.max_batch_size = getattr(settings, "REALTIME_BATCH_SIZE", 50)
        self.cache_timeout = getattr(
            settings, "REALTIME_CACHE_TIMEOUT", 300
        )  # 5 minutes
        self.is_running = False
        self.update_task = None

    async def start(self):
        """Start the real-time price feed service."""
        if self.is_running:
            logger.warning("Price feed service is already running")
            return

        self.is_running = True
        self.update_task = asyncio.create_task(self._price_update_loop())
        logger.info("Price feed service started")

    async def stop(self):
        """Stop the real-time price feed service."""
        self.is_running = False
        if self.update_task:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass
        logger.info("Price feed service stopped")

    async def _price_update_loop(self):
        """Main loop for price updates."""
        while self.is_running:
            try:
                await self._update_subscribed_assets()
                await asyncio.sleep(self.update_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in price update loop: %s", e)
                await asyncio.sleep(self.update_interval)

    async def _update_subscribed_assets(self):
        """Update prices for all subscribed assets."""
        # Get all assets that have active subscriptions
        subscribed_symbols = set(connection_manager.asset_subscriptions.keys())

        # Also get assets from subscribed portfolios
        portfolio_assets = await self._get_portfolio_assets()
        subscribed_symbols.update(portfolio_assets)

        if not subscribed_symbols:
            return

        logger.debug(
            f"Updating prices for {len(subscribed_symbols)} subscribed assets"
        )

        # Process assets in batches to avoid overwhelming the API
        symbol_batches = [
            list(subscribed_symbols)[i : i + self.max_batch_size]
            for i in range(0, len(subscribed_symbols), self.max_batch_size)
        ]

        for batch in symbol_batches:
            await self._update_asset_batch(batch)

    @staticmethod
    async def _get_portfolio_assets() -> Set[str]:
        """Get all asset symbols from subscribed portfolios."""
        # Skip if portfolio models are not available
        if Portfolio is None or Position is None:
            logger.debug(
                "Portfolio models not available, returning empty asset set"
            )
            return set()

        assets = set()
        for portfolio_id in connection_manager.portfolio_subscriptions.keys():
            try:
                portfolio = await Portfolio.objects.select_related().aget(
                    id=portfolio_id
                )
                portfolio_positions = Position.objects.filter(
                    portfolio=portfolio, quantity__gt=0
                ).select_related("asset")

                async for position in portfolio_positions:
                    assets.add(position.asset.symbol)
            except Portfolio.DoesNotExist:
                logger.warning("Portfolio %s not found", portfolio_id)
            except Exception as e:
                logger.error(
                    f"Error getting assets for portfolio {portfolio_id}: {e}"
                )

        return assets

    async def _update_asset_batch(self, symbols: List[str]):
        """Update prices for a batch of asset symbols."""
        try:
            # Get current prices from data sources
            price_updates = await self._fetch_price_updates(symbols)

            # Update database and broadcast changes
            for symbol, price_data in price_updates.items():
                await self._process_price_update(symbol, price_data)

        except Exception as e:
            logger.error("Error updating asset batch %s: %s", symbols, e)

    async def _fetch_price_updates(
        self, symbols: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Fetch price updates from data sources.

        Args:
            symbols: List of asset symbols to update

        Returns:
            Dictionary mapping symbols to price data
        """
        price_updates = {}

        for symbol in symbols:
            try:
                # Check cache first
                cache_key = f"realtime_price_{symbol}"
                cached_price = cache.get(cache_key)

                if cached_price:
                    price_updates[symbol] = cached_price
                    continue

                # Fetch from data source
                price_data = data_source_manager.get_current_price(symbol)

                if price_data:
                    update_data = {
                        "symbol": symbol,
                        "current_price": price_data.current_price,
                        "change": price_data.change,
                        "change_percent": price_data.change_percent,
                        "volume": price_data.volume,
                        "high": price_data.high,
                        "low": price_data.low,
                        "open": price_data.open,
                        "timestamp": datetime.now(),
                        "source": price_data.source,
                    }

                    price_updates[symbol] = update_data

                    # Cache the update
                    cache.set(cache_key, update_data, self.cache_timeout)

            except Exception as e:
                logger.error("Error fetching price for %s: %s", symbol, e)

        return price_updates

    async def _process_price_update(
        self, symbol: str, price_data: Dict[str, Any]
    ):
        """
        Process a price update and broadcast to subscribers.

        Args:
            symbol: Asset symbol
            price_data: Price update data
        """
        try:
            # Update database
            await self._update_asset_price(symbol, price_data)

            # Broadcast to asset subscribers
            await self._broadcast_asset_update(symbol, price_data)

            # Update affected portfolios
            await self._update_portfolio_values(symbol, price_data)

        except Exception as e:
            logger.error("Error processing price update for %s: %s", symbol, e)

    @staticmethod
    async def _update_asset_price(symbol: str, price_data: Dict[str, Any]):
        """Update asset price in the database."""
        # Skip if Asset model is not available
        if Asset is None:
            logger.debug(
                f"Asset model not available, skipping price update for {symbol}"
            )
            return

        try:
            asset = await Asset.objects.aget(symbol=symbol)

            # Update current price
            asset.current_price = Decimal(str(price_data["current_price"]))
            asset.last_updated = timezone.now()
            await asset.asave()

            # Create price history entry (only if PriceHistory model is available)
            try:
                await PriceHistory.objects.acreate(
                    asset=asset,
                    date=timezone.now().date(),
                    open=Decimal(
                        str(
                            price_data.get("open", price_data["current_price"])
                        )
                    ),
                    high=Decimal(
                        str(
                            price_data.get("high", price_data["current_price"])
                        )
                    ),
                    low=Decimal(
                        str(price_data.get("low", price_data["current_price"]))
                    ),
                    close=Decimal(str(price_data["current_price"])),
                    volume=price_data.get("volume", 0),
                    source=price_data.get("source", "realtime"),
                )
            except (NotImplementedError, AttributeError):
                # PriceHistory model is not available or implemented
                logger.debug(
                    f"PriceHistory not available, skipping price history for {symbol}"
                )

        except Asset.DoesNotExist:
            logger.warning("Asset %s not found in database", symbol)
        except Exception as e:
            logger.error("Error updating asset price for %s: %s", symbol, e)

    @staticmethod
    async def _broadcast_asset_update(symbol: str, price_data: Dict[str, Any]):
        """Broadcast asset price update to subscribers."""
        subscribers = connection_manager.get_asset_subscribers(symbol)

        if not subscribers:
            return

        message = encode_message(
            "asset_update",
            {
                "symbol": symbol,
                "price": price_data["current_price"],
                "change": price_data.get("change"),
                "change_percent": price_data.get("change_percent"),
                "volume": price_data.get("volume"),
                "high": price_data.get("high"),
                "low": price_data.get("low"),
                "timestamp": price_data["timestamp"],
            },
        )

        logger.debug(
            f"Broadcasting asset update for {symbol} to {len(subscribers)} subscribers"
        )

        # Note: Actual message sending would be handled by the WebSocket handler
        # This is just preparing the message for broadcast

    async def _update_portfolio_values(
        self, symbol: str, price_data: Dict[str, Any]
    ):
        """Update portfolio values affected by the price change."""
        # Skip if portfolio models are not available
        if Position is None or Portfolio is None:
            logger.debug(
                f"Portfolio models not available, skipping portfolio updates for {symbol}"
            )
            return

        try:
            # Find portfolios that contain this asset
            affected_portfolios = set()

            async for position in Position.objects.select_related(
                "portfolio", "asset"
            ).filter(asset__symbol=symbol, quantity__gt=0):
                affected_portfolios.add(position.portfolio.id)

            # Update and broadcast portfolio values
            for portfolio_id in affected_portfolios:
                await self._broadcast_portfolio_update(portfolio_id)

        except Exception as e:
            logger.error(
                "Error updating portfolio values for %s: %s", symbol, e
            )

    async def _broadcast_portfolio_update(self, portfolio_id: int):
        """Broadcast portfolio value update to subscribers."""
        # Skip if Portfolio model is not available
        if Portfolio is None:
            logger.debug(
                f"Portfolio model not available, skipping broadcast for portfolio {portfolio_id}"
            )
            return

        subscribers = connection_manager.get_portfolio_subscribers(
            portfolio_id
        )

        if not subscribers:
            return

        try:
            portfolio = await Portfolio.objects.aget(id=portfolio_id)

            # Calculate portfolio metrics
            portfolio_value = await self._calculate_portfolio_value(portfolio)
            daily_change = await self._calculate_daily_change(portfolio)

            message = encode_message(
                "portfolio_update",
                {
                    "portfolio_id": portfolio_id,
                    "name": portfolio.name,
                    "total_value": portfolio_value,
                    "daily_change": daily_change["amount"],
                    "daily_change_percent": daily_change["percent"],
                    "updated_at": datetime.now(),
                },
            )

            logger.debug(
                f"Broadcasting portfolio update for {portfolio_id} to {len(subscribers)} subscribers"
            )

        except Portfolio.DoesNotExist:
            logger.warning("Portfolio %s not found", portfolio_id)
        except Exception as e:
            logger.error(
                f"Error broadcasting portfolio update for {portfolio_id}: {e}"
            )

    @staticmethod
    async def _calculate_portfolio_value(portfolio) -> Decimal:
        """Calculate current portfolio value."""
        # Skip if Position model is not available
        if Position is None:
            logger.debug(
                "Position model not available, returning zero portfolio value"
            )
            return Decimal("0")

        total_value = Decimal("0")

        async for position in Position.objects.select_related("asset").filter(
            portfolio=portfolio, quantity__gt=0
        ):
            if position.asset.current_price:
                position_value = (
                    position.quantity * position.asset.current_price
                )
                total_value += position_value

        return total_value

    async def _calculate_daily_change(
        self, portfolio: Portfolio
    ) -> Dict[str, Decimal]:
        """Calculate daily change for portfolio."""
        # This is a simplified calculation
        # In a real implementation, you'd compare with yesterday's closing value
        current_value = await self._calculate_portfolio_value(portfolio)

        # For now, return placeholder values
        # You would implement proper daily change calculation here
        return {"amount": Decimal("0"), "percent": Decimal("0")}

    @staticmethod
    async def subscribe_to_asset(connection_id: str, symbol: str):
        """Subscribe a connection to asset updates and send current price."""
        await connection_manager.subscribe_to_asset(connection_id, symbol)

        # Send current price immediately (if Asset model is available)
        if Asset is None:
            logger.debug(
                f"Asset model not available, skipping initial price for {symbol}"
            )
            return

        try:
            asset = await Asset.objects.aget(symbol=symbol)
            if asset.current_price:
                message = encode_message(
                    "asset_update",
                    {
                        "symbol": symbol,
                        "price": asset.current_price,
                        "timestamp": datetime.now(),
                    },
                )
                # Message would be sent to the specific connection

        except Asset.DoesNotExist:
            logger.warning("Asset %s not found for subscription", symbol)

    async def subscribe_to_portfolio(
        self, connection_id: str, portfolio_id: int
    ):
        """Subscribe a connection to portfolio updates and send current value."""
        await connection_manager.subscribe_to_portfolio(
            connection_id, portfolio_id
        )

        # Send current portfolio value immediately
        await self._broadcast_portfolio_update(portfolio_id)


# Global price feed service instance
price_feed_service = PriceFeedService()


async def start_price_feed():
    """Start the price feed service."""
    await price_feed_service.start()


async def stop_price_feed():
    """Stop the price feed service."""
    await price_feed_service.stop()


async def start_realtime_service(
    mode: str = "polling", update_interval: int = 15
):
    """Start the realtime service."""
    global realtime_service
    realtime_service = RealtimeService(
        mode=mode, update_interval=update_interval
    )
    await realtime_service.start()


async def stop_realtime_service():
    """Stop the realtime service."""
    if realtime_service:
        await realtime_service.stop()


def subscribe_to_prices(symbols: List[str], callback: Callable):
    """
    Subscribe to price updates (sync wrapper).

    Args:
        symbols: List of asset symbols to subscribe to
        callback: Function to call with PricePoint objects
    """
    import asyncio

    loop = None
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're in an async context, schedule the coroutine and return the task
            return asyncio.create_task(realtime_service.subscribe(symbols, callback))
        else:
            # If we're not in an async context, run it
            loop.run_until_complete(
                realtime_service.subscribe(symbols, callback)
            )
    except RuntimeError:
        # No event loop running, create one
        new_loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(new_loop)
            new_loop.run_until_complete(
                realtime_service.subscribe(symbols, callback)
            )
        finally:
            new_loop.close()
