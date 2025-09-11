"""
Real-time price feed service for WebSocket updates.

This module handles live market data streaming, price updates,
and integration with multiple data sources for real-time feeds.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Set, Any
from datetime import datetime, timedelta
from decimal import Decimal

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

# Mock PriceHistory since it doesn't exist yet
class PriceHistory:
    """Mock PriceHistory model for compatibility."""
    @classmethod
    def objects(cls):
        return None
try:
    from personal_finance.data_sources.services import data_source_manager
except ImportError:
    data_source_manager = None

try:
    from personal_finance.realtime.connections import connection_manager, encode_message
except ImportError:
    connection_manager = None
    def encode_message(data):
        return data

logger = logging.getLogger(__name__)


class PriceFeedService:
    """
    Real-time price feed service for live market data updates.
    
    Manages price streaming from multiple data sources and broadcasts
    updates to subscribed WebSocket connections.
    """
    
    def __init__(self):
        """Initialize the price feed service."""
        self.update_interval = getattr(settings, 'REALTIME_UPDATE_INTERVAL', 30)  # seconds
        self.max_batch_size = getattr(settings, 'REALTIME_BATCH_SIZE', 50)
        self.cache_timeout = getattr(settings, 'REALTIME_CACHE_TIMEOUT', 300)  # 5 minutes
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
                logger.error(f"Error in price update loop: {e}")
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
        
        logger.debug(f"Updating prices for {len(subscribed_symbols)} subscribed assets")
        
        # Process assets in batches to avoid overwhelming the API
        symbol_batches = [
            list(subscribed_symbols)[i:i + self.max_batch_size]
            for i in range(0, len(subscribed_symbols), self.max_batch_size)
        ]
        
        for batch in symbol_batches:
            await self._update_asset_batch(batch)
    
    async def _get_portfolio_assets(self) -> Set[str]:
        """Get all asset symbols from subscribed portfolios."""
        assets = set()
        for portfolio_id in connection_manager.portfolio_subscriptions.keys():
            try:
                portfolio = await Portfolio.objects.select_related().aget(id=portfolio_id)
                portfolio_positions = Position.objects.filter(
                    portfolio=portfolio,
                    quantity__gt=0
                ).select_related('asset')
                
                async for position in portfolio_positions:
                    assets.add(position.asset.symbol)
            except Portfolio.DoesNotExist:
                logger.warning(f"Portfolio {portfolio_id} not found")
            except Exception as e:
                logger.error(f"Error getting assets for portfolio {portfolio_id}: {e}")
        
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
            logger.error(f"Error updating asset batch {symbols}: {e}")
    
    async def _fetch_price_updates(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
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
                        'symbol': symbol,
                        'current_price': price_data.current_price,
                        'change': price_data.change,
                        'change_percent': price_data.change_percent,
                        'volume': price_data.volume,
                        'high': price_data.high,
                        'low': price_data.low,
                        'open': price_data.open,
                        'timestamp': datetime.now(),
                        'source': price_data.source
                    }
                    
                    price_updates[symbol] = update_data
                    
                    # Cache the update
                    cache.set(cache_key, update_data, self.cache_timeout)
                    
            except Exception as e:
                logger.error(f"Error fetching price for {symbol}: {e}")
        
        return price_updates
    
    async def _process_price_update(self, symbol: str, price_data: Dict[str, Any]):
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
            logger.error(f"Error processing price update for {symbol}: {e}")
    
    async def _update_asset_price(self, symbol: str, price_data: Dict[str, Any]):
        """Update asset price in the database."""
        try:
            asset = await Asset.objects.aget(symbol=symbol)
            
            # Update current price
            asset.current_price = Decimal(str(price_data['current_price']))
            asset.last_updated = timezone.now()
            await asset.asave()
            
            # Create price history entry
            await PriceHistory.objects.acreate(
                asset=asset,
                date=timezone.now().date(),
                open=Decimal(str(price_data.get('open', price_data['current_price']))),
                high=Decimal(str(price_data.get('high', price_data['current_price']))),
                low=Decimal(str(price_data.get('low', price_data['current_price']))),
                close=Decimal(str(price_data['current_price'])),
                volume=price_data.get('volume', 0),
                source=price_data.get('source', 'realtime')
            )
            
        except Asset.DoesNotExist:
            logger.warning(f"Asset {symbol} not found in database")
        except Exception as e:
            logger.error(f"Error updating asset price for {symbol}: {e}")
    
    async def _broadcast_asset_update(self, symbol: str, price_data: Dict[str, Any]):
        """Broadcast asset price update to subscribers."""
        subscribers = connection_manager.get_asset_subscribers(symbol)
        
        if not subscribers:
            return
        
        message = encode_message('asset_update', {
            'symbol': symbol,
            'price': price_data['current_price'],
            'change': price_data.get('change'),
            'change_percent': price_data.get('change_percent'),
            'volume': price_data.get('volume'),
            'high': price_data.get('high'),
            'low': price_data.get('low'),
            'timestamp': price_data['timestamp']
        })
        
        logger.debug(f"Broadcasting asset update for {symbol} to {len(subscribers)} subscribers")
        
        # Note: Actual message sending would be handled by the WebSocket handler
        # This is just preparing the message for broadcast
        
    async def _update_portfolio_values(self, symbol: str, price_data: Dict[str, Any]):
        """Update portfolio values affected by the price change."""
        try:
            # Find portfolios that contain this asset
            affected_portfolios = set()
            
            async for position in Position.objects.select_related('portfolio', 'asset').filter(
                asset__symbol=symbol,
                quantity__gt=0
            ):
                affected_portfolios.add(position.portfolio.id)
            
            # Update and broadcast portfolio values
            for portfolio_id in affected_portfolios:
                await self._broadcast_portfolio_update(portfolio_id)
                
        except Exception as e:
            logger.error(f"Error updating portfolio values for {symbol}: {e}")
    
    async def _broadcast_portfolio_update(self, portfolio_id: int):
        """Broadcast portfolio value update to subscribers."""
        subscribers = connection_manager.get_portfolio_subscribers(portfolio_id)
        
        if not subscribers:
            return
        
        try:
            portfolio = await Portfolio.objects.aget(id=portfolio_id)
            
            # Calculate portfolio metrics
            portfolio_value = await self._calculate_portfolio_value(portfolio)
            daily_change = await self._calculate_daily_change(portfolio)
            
            message = encode_message('portfolio_update', {
                'portfolio_id': portfolio_id,
                'name': portfolio.name,
                'total_value': portfolio_value,
                'daily_change': daily_change['amount'],
                'daily_change_percent': daily_change['percent'],
                'updated_at': datetime.now()
            })
            
            logger.debug(f"Broadcasting portfolio update for {portfolio_id} to {len(subscribers)} subscribers")
            
        except Portfolio.DoesNotExist:
            logger.warning(f"Portfolio {portfolio_id} not found")
        except Exception as e:
            logger.error(f"Error broadcasting portfolio update for {portfolio_id}: {e}")
    
    async def _calculate_portfolio_value(self, portfolio: Portfolio) -> Decimal:
        """Calculate current portfolio value."""
        total_value = Decimal('0')
        
        async for position in Position.objects.select_related('asset').filter(
            portfolio=portfolio,
            quantity__gt=0
        ):
            if position.asset.current_price:
                position_value = position.quantity * position.asset.current_price
                total_value += position_value
        
        return total_value
    
    async def _calculate_daily_change(self, portfolio: Portfolio) -> Dict[str, Decimal]:
        """Calculate daily change for portfolio."""
        # This is a simplified calculation
        # In a real implementation, you'd compare with yesterday's closing value
        current_value = await self._calculate_portfolio_value(portfolio)
        
        # For now, return placeholder values
        # You would implement proper daily change calculation here
        return {
            'amount': Decimal('0'),
            'percent': Decimal('0')
        }
    
    async def subscribe_to_asset(self, connection_id: str, symbol: str):
        """Subscribe a connection to asset updates and send current price."""
        await connection_manager.subscribe_to_asset(connection_id, symbol)
        
        # Send current price immediately
        try:
            asset = await Asset.objects.aget(symbol=symbol)
            if asset.current_price:
                message = encode_message('asset_update', {
                    'symbol': symbol,
                    'price': asset.current_price,
                    'timestamp': datetime.now()
                })
                # Message would be sent to the specific connection
                
        except Asset.DoesNotExist:
            logger.warning(f"Asset {symbol} not found for subscription")
    
    async def subscribe_to_portfolio(self, connection_id: str, portfolio_id: int):
        """Subscribe a connection to portfolio updates and send current value."""
        await connection_manager.subscribe_to_portfolio(connection_id, portfolio_id)
        
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