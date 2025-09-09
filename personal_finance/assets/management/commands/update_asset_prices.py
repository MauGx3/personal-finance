"""Management command to update asset prices from external data sources."""

import logging
from typing import List, Optional
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from personal_finance.assets.models import Asset, PriceHistory
from personal_finance.data_sources.services import data_source_manager

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Update asset prices from external data sources.
    
    This command fetches current price data for all active assets
    and optionally updates historical price data. Includes error
    handling and logging for production use.
    
    Usage:
        python manage.py update_asset_prices
        python manage.py update_asset_prices --symbols AAPL MSFT GOOGL
        python manage.py update_asset_prices --historical --days 30
        python manage.py update_asset_prices --force-update
    """
    
    help = 'Update asset prices from external data sources'
    
    def add_arguments(self, parser):
        """Add command-line arguments."""
        parser.add_argument(
            '--symbols',
            nargs='+',
            help='Specific symbols to update (default: all active assets)',
        )
        parser.add_argument(
            '--historical',
            action='store_true',
            help='Update historical price data',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days of historical data to fetch (default: 30)',
        )
        parser.add_argument(
            '--force-update',
            action='store_true',
            help='Force update even if recently updated',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Number of assets to process in each batch (default: 50)',
        )
    
    def handle(self, *args, **options):
        """Execute the command."""
        self.verbosity = options['verbosity']
        self.dry_run = options['dry_run']
        
        if self.dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        # Get assets to update
        assets = self._get_assets_to_update(options['symbols'])
        
        if not assets:
            self.stdout.write(
                self.style.WARNING('No assets found to update')
            )
            return
        
        self.stdout.write(
            f'Found {len(assets)} assets to update'
        )
        
        # Update current prices
        updated_count = self._update_current_prices(
            assets, 
            options['force_update'],
            options['batch_size']
        )
        
        # Update historical data if requested
        if options['historical']:
            historical_count = self._update_historical_data(
                assets,
                options['days'],
                options['batch_size']
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Updated historical data for {historical_count} assets'
                )
            )
        
        # Show data source status
        self._show_data_source_status()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated prices for {updated_count} assets'
            )
        )
    
    def _get_assets_to_update(self, symbols: Optional[List[str]]) -> List[Asset]:
        """Get list of assets to update.
        
        Args:
            symbols: Optional list of specific symbols to update
            
        Returns:
            List of Asset objects to update
        """
        if symbols:
            assets = Asset.objects.filter(
                symbol__in=symbols,
                is_active=True
            )
            
            missing_symbols = set(symbols) - set(
                assets.values_list('symbol', flat=True)
            )
            if missing_symbols:
                self.stdout.write(
                    self.style.WARNING(
                        f'Symbols not found: {", ".join(missing_symbols)}'
                    )
                )
        else:
            assets = Asset.objects.filter(
                is_active=True,
                is_tradeable=True
            )
        
        return list(assets)
    
    def _update_current_prices(self, 
                             assets: List[Asset], 
                             force_update: bool,
                             batch_size: int) -> int:
        """Update current prices for assets.
        
        Args:
            assets: List of assets to update
            force_update: Whether to force update even if recently updated
            batch_size: Number of assets to process per batch
            
        Returns:
            Number of assets successfully updated
        """
        updated_count = 0
        cutoff_time = timezone.now() - timedelta(minutes=15)
        
        # Filter assets that need updating
        if not force_update:
            assets_to_update = [
                asset for asset in assets
                if (asset.last_price_update is None or 
                    asset.last_price_update < cutoff_time)
            ]
        else:
            assets_to_update = assets
        
        if self.verbosity >= 2:
            self.stdout.write(
                f'Updating current prices for {len(assets_to_update)} assets'
            )
        
        # Process in batches to avoid overwhelming APIs
        for i in range(0, len(assets_to_update), batch_size):
            batch = assets_to_update[i:i + batch_size]
            
            if self.verbosity >= 2:
                symbols = [asset.symbol for asset in batch]
                self.stdout.write(
                    f'Processing batch: {", ".join(symbols)}'
                )
            
            for asset in batch:
                try:
                    if self._update_asset_price(asset):
                        updated_count += 1
                        
                        if self.verbosity >= 2:
                            self.stdout.write(
                                f'Updated {asset.symbol}: ${asset.current_price}'
                            )
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error updating {asset.symbol}: {e}'
                        )
                    )
                    logger.error(f'Error updating {asset.symbol}: {e}')
        
        return updated_count
    
    def _update_asset_price(self, asset: Asset) -> bool:
        """Update price for a single asset.
        
        Args:
            asset: Asset to update
            
        Returns:
            True if update was successful, False otherwise
        """
        if self.dry_run:
            self.stdout.write(f'Would update {asset.symbol}')
            return True
        
        try:
            price_data = data_source_manager.get_current_price(asset.symbol)
            
            if price_data:
                with transaction.atomic():
                    asset.update_price_data(
                        price=price_data.current_price,
                        volume=price_data.volume,
                        day_high=price_data.day_high,
                        day_low=price_data.day_low,
                        source=f"auto_update_{price_data.last_updated.strftime('%Y%m%d')}"
                    )
                
                return True
            else:
                if self.verbosity >= 2:
                    self.stdout.write(
                        self.style.WARNING(
                            f'No price data available for {asset.symbol}'
                        )
                    )
                return False
                
        except Exception as e:
            if self.verbosity >= 1:
                self.stdout.write(
                    self.style.ERROR(
                        f'Failed to update {asset.symbol}: {e}'
                    )
                )
            return False
    
    def _update_historical_data(self, 
                              assets: List[Asset], 
                              days: int,
                              batch_size: int) -> int:
        """Update historical price data for assets.
        
        Args:
            assets: List of assets to update
            days: Number of days of historical data to fetch
            batch_size: Number of assets to process per batch
            
        Returns:
            Number of assets with historical data updated
        """
        updated_count = 0
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        if self.verbosity >= 2:
            self.stdout.write(
                f'Updating historical data from {start_date} to {end_date}'
            )
        
        for i in range(0, len(assets), batch_size):
            batch = assets[i:i + batch_size]
            
            for asset in batch:
                try:
                    if self._update_asset_historical_data(asset, start_date, end_date):
                        updated_count += 1
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error updating historical data for {asset.symbol}: {e}'
                        )
                    )
        
        return updated_count
    
    def _update_asset_historical_data(self, 
                                    asset: Asset, 
                                    start_date, 
                                    end_date) -> bool:
        """Update historical data for a single asset.
        
        Args:
            asset: Asset to update
            start_date: Start date for historical data
            end_date: End date for historical data
            
        Returns:
            True if update was successful, False otherwise
        """
        if self.dry_run:
            self.stdout.write(f'Would update historical data for {asset.symbol}')
            return True
        
        try:
            historical_data = data_source_manager.get_historical_data(
                asset.symbol, start_date, end_date
            )
            
            if historical_data:
                created_count = 0
                updated_count = 0
                
                for data_point in historical_data:
                    price_history, created = PriceHistory.objects.update_or_create(
                        asset=asset,
                        date=data_point.date,
                        defaults={
                            'open_price': data_point.open_price,
                            'high_price': data_point.high_price,
                            'low_price': data_point.low_price,
                            'close_price': data_point.close_price,
                            'adjusted_close': data_point.adjusted_close,
                            'volume': data_point.volume,
                            'dividend_amount': data_point.dividend_amount,
                            'split_ratio': data_point.split_ratio,
                            'data_source': 'auto_update_historical',
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                
                if self.verbosity >= 2:
                    self.stdout.write(
                        f'Historical data for {asset.symbol}: '
                        f'{created_count} new, {updated_count} updated'
                    )
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f'Historical data update error for {asset.symbol}: {e}')
            return False
    
    def _show_data_source_status(self):
        """Show status of all data sources."""
        if self.verbosity >= 1:
            status = data_source_manager.get_source_status()
            
            self.stdout.write('\nData Source Status:')
            self.stdout.write('-' * 50)
            
            for source_name, source_status in status.items():
                status_color = self.style.SUCCESS if source_status['available'] else self.style.ERROR
                availability = 'Available' if source_status['available'] else 'Unavailable'
                
                self.stdout.write(
                    f'{source_name}: {status_color(availability)} '
                    f'(Failures: {source_status["failures"]})'
                )