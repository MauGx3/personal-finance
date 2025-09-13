"""Management command to demonstrate Polars data analysis capabilities.

This command showcases the enhanced data processing capabilities using Polars
and other modern data analysis libraries as specified in the S.C.A.F.F. structure.
"""

import logging
from decimal import Decimal
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

# Graceful imports for new data analysis libraries
try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False
    pl = None

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

try:
    from personal_finance.data_sources.polars_integration import polars_processor
    POLARS_INTEGRATION_AVAILABLE = True
except ImportError:
    POLARS_INTEGRATION_AVAILABLE = False
    polars_processor = None

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Management command for Polars data analysis demonstration."""
    
    help = 'Demonstrate enhanced data analysis capabilities with Polars and modern libraries'
    
    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            '--demo-type',
            type=str,
            choices=['portfolio', 'technical', 'performance', 'all'],
            default='all',
            help='Type of data analysis demo to run'
        )
        
        parser.add_argument(
            '--symbols',
            nargs='+',
            default=['AAPL', 'GOOGL', 'MSFT', 'TSLA'],
            help='Stock symbols for demonstration'
        )
        
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Number of days of historical data to analyze'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be analyzed without performing actual calculations'
        )
    
    def handle(self, *args, **options):
        """Execute the command."""
        self.verbosity = options['verbosity']
        demo_type = options['demo_type']
        symbols = options['symbols']
        days = options['days']
        dry_run = options['dry_run']
        
        if self.verbosity >= 1:
            self.stdout.write(
                self.style.SUCCESS(
                    '=== Enhanced Data Analysis Demo ==='
                )
            )
        
        # Check library availability
        self._check_library_availability()
        
        if dry_run:
            self._show_dry_run_info(demo_type, symbols, days)
            return
        
        # Run selected demos
        if demo_type in ['portfolio', 'all']:
            self._demo_portfolio_analysis(symbols)
        
        if demo_type in ['technical', 'all']:
            self._demo_technical_analysis(symbols, days)
        
        if demo_type in ['performance', 'all']:
            self._demo_performance_analysis(symbols, days)
        
        if self.verbosity >= 1:
            self.stdout.write(
                self.style.SUCCESS(
                    '=== Demo completed successfully ==='
                )
            )
    
    def _check_library_availability(self):
        """Check availability of data analysis libraries."""
        if self.verbosity >= 1:
            self.stdout.write('📊 Checking data analysis libraries...')
        
        libraries = [
            ('Polars', POLARS_AVAILABLE),
            ('Pandas', PANDAS_AVAILABLE),
            ('Polars Integration', POLARS_INTEGRATION_AVAILABLE),
        ]
        
        for name, available in libraries:
            status = '✅ Available' if available else '❌ Not available'
            if self.verbosity >= 2:
                self.stdout.write(f'  {name}: {status}')
        
        if not any(available for _, available in libraries[:2]):
            raise CommandError(
                'No data analysis libraries available. '
                'Install polars or pandas: pip install polars pandas'
            )
    
    def _show_dry_run_info(self, demo_type: str, symbols: List[str], days: int):
        """Show what would be analyzed in dry run mode."""
        self.stdout.write(
            self.style.WARNING(
                '🔍 DRY RUN MODE - No actual analysis will be performed'
            )
        )
        
        self.stdout.write(f'Demo type: {demo_type}')
        self.stdout.write(f'Symbols: {", ".join(symbols)}')
        self.stdout.write(f'Historical days: {days}')
        
        if demo_type in ['portfolio', 'all']:
            self.stdout.write('📈 Would run portfolio analysis demo')
        
        if demo_type in ['technical', 'all']:
            self.stdout.write('📊 Would run technical analysis demo')
        
        if demo_type in ['performance', 'all']:
            self.stdout.write('⚡ Would run performance analysis demo')
    
    def _demo_portfolio_analysis(self, symbols: List[str]):
        """Demonstrate portfolio analysis capabilities."""
        if self.verbosity >= 1:
            self.stdout.write(
                self.style.HTTP_INFO(
                    '📈 Portfolio Analysis Demo'
                )
            )
        
        if not POLARS_INTEGRATION_AVAILABLE:
            self.stdout.write(
                self.style.WARNING(
                    'Polars integration not available, skipping portfolio demo'
                )
            )
            return
        
        # Create sample portfolio data
        sample_holdings = self._create_sample_holdings(symbols)
        
        if self.verbosity >= 2:
            self.stdout.write(f'Sample holdings created: {len(sample_holdings)} positions')
        
        # Calculate portfolio metrics using enhanced data processor
        try:
            metrics = polars_processor.calculate_portfolio_metrics(sample_holdings)
            
            if self.verbosity >= 1:
                self.stdout.write('Portfolio Metrics:')
                for key, value in metrics.items():
                    if isinstance(value, (int, float)):
                        if 'percentage' in key:
                            formatted_value = f'{value:.2f}%'
                        elif 'value' in key or 'cost' in key or 'return' in key:
                            formatted_value = f'${value:,.2f}'
                        else:
                            formatted_value = f'{value:,}'
                    else:
                        formatted_value = str(value)
                    
                    self.stdout.write(f'  {key}: {formatted_value}')
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Portfolio analysis error: {e}')
            )
            logger.error(f'Portfolio analysis error: {e}')
    
    def _demo_technical_analysis(self, symbols: List[str], days: int):
        """Demonstrate technical analysis capabilities."""
        if self.verbosity >= 1:
            self.stdout.write(
                self.style.HTTP_INFO(
                    '📊 Technical Analysis Demo'
                )
            )
        
        if not POLARS_INTEGRATION_AVAILABLE:
            self.stdout.write(
                self.style.WARNING(
                    'Polars integration not available, skipping technical demo'
                )
            )
            return
        
        # Create sample price data
        sample_data = self._create_sample_price_data(symbols[0], days)
        
        if self.verbosity >= 2:
            self.stdout.write(f'Sample price data created: {len(sample_data)} days')
        
        try:
            # Create DataFrame using enhanced processor
            df = polars_processor.create_price_dataframe(sample_data)
            
            # Calculate moving averages
            df_with_ma = polars_processor.calculate_moving_averages(df)
            
            # Calculate technical indicators
            df_with_indicators = polars_processor.calculate_technical_indicators(df_with_ma)
            
            if self.verbosity >= 1:
                # Show sample of calculated indicators
                if POLARS_AVAILABLE and hasattr(df_with_indicators, 'tail'):
                    # Polars DataFrame
                    sample_rows = df_with_indicators.tail(5)
                    self.stdout.write('Latest technical indicators (Polars):')
                    self.stdout.write(str(sample_rows))
                elif PANDAS_AVAILABLE and hasattr(df_with_indicators, 'tail'):
                    # Pandas DataFrame
                    sample_rows = df_with_indicators.tail()
                    self.stdout.write('Latest technical indicators (Pandas):')
                    self.stdout.write(str(sample_rows))
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Technical analysis error: {e}')
            )
            logger.error(f'Technical analysis error: {e}')
    
    def _demo_performance_analysis(self, symbols: List[str], days: int):
        """Demonstrate performance analysis capabilities."""
        if self.verbosity >= 1:
            self.stdout.write(
                self.style.HTTP_INFO(
                    '⚡ Performance Analysis Demo'
                )
            )
        
        # Demonstrate library performance differences
        self._benchmark_dataframe_operations(symbols, days)
        
        # Show available modern data analysis capabilities
        self._show_available_capabilities()
    
    def _benchmark_dataframe_operations(self, symbols: List[str], days: int):
        """Benchmark DataFrame operations between libraries."""
        if not (POLARS_AVAILABLE or PANDAS_AVAILABLE):
            self.stdout.write(
                self.style.WARNING(
                    'No DataFrame libraries available for benchmarking'
                )
            )
            return
        
        # Create sample data for benchmarking
        sample_data = []
        for symbol in symbols:
            sample_data.extend(self._create_sample_price_data(symbol, days))
        
        if self.verbosity >= 2:
            self.stdout.write(f'Benchmarking with {len(sample_data)} data points')
        
        # Time DataFrame creation and basic operations
        import time
        
        if POLARS_AVAILABLE:
            start_time = time.time()
            pl_df = pl.DataFrame(sample_data)
            pl_df_filtered = pl_df.filter(pl.col('volume') > 1000000)
            pl_time = time.time() - start_time
            
            if self.verbosity >= 1:
                self.stdout.write(f'Polars processing time: {pl_time:.4f}s')
        
        if PANDAS_AVAILABLE:
            start_time = time.time()
            pd_df = pd.DataFrame(sample_data)
            pd_df_filtered = pd_df[pd_df['volume'] > 1000000]
            pd_time = time.time() - start_time
            
            if self.verbosity >= 1:
                self.stdout.write(f'Pandas processing time: {pd_time:.4f}s')
    
    def _show_available_capabilities(self):
        """Show available modern data analysis capabilities."""
        if self.verbosity >= 1:
            self.stdout.write('🚀 Available Modern Data Analysis Capabilities:')
        
        capabilities = [
            ('Polars DataFrame processing', POLARS_AVAILABLE),
            ('Enhanced portfolio analytics', POLARS_INTEGRATION_AVAILABLE),
            ('Technical indicator calculations', POLARS_INTEGRATION_AVAILABLE),
            ('High-performance data processing', POLARS_AVAILABLE),
            ('Lazy evaluation for large datasets', POLARS_AVAILABLE),
        ]
        
        for capability, available in capabilities:
            status = '✅' if available else '❌'
            if self.verbosity >= 2:
                self.stdout.write(f'  {status} {capability}')
    
    def _create_sample_holdings(self, symbols: List[str]) -> List[Dict]:
        """Create sample portfolio holdings for demonstration."""
        import random
        
        holdings = []
        for i, symbol in enumerate(symbols):
            holdings.append({
                'symbol': symbol,
                'quantity': random.randint(10, 100),
                'cost_basis': random.uniform(50, 500) * random.randint(10, 100),
                'current_value': random.uniform(60, 600) * random.randint(10, 100),
                'purchase_date': (timezone.now() - timedelta(days=random.randint(30, 365))).date(),
            })
        
        return holdings
    
    def _create_sample_price_data(self, symbol: str, days: int) -> List[Dict]:
        """Create sample price data for demonstration."""
        import random
        
        data = []
        base_price = random.uniform(50, 500)
        current_date = timezone.now().date()
        
        for i in range(days):
            # Simulate price movement
            price_change = random.uniform(-0.05, 0.05)  # ±5% daily change
            base_price *= (1 + price_change)
            
            # Ensure positive prices
            base_price = max(base_price, 1.0)
            
            # Create OHLCV data
            open_price = base_price * random.uniform(0.99, 1.01)
            high_price = base_price * random.uniform(1.0, 1.03)
            low_price = base_price * random.uniform(0.97, 1.0)
            close_price = base_price
            
            data.append({
                'symbol': symbol,
                'date': (current_date - timedelta(days=days-i-1)).isoformat(),
                'open_price': round(open_price, 2),
                'high_price': round(high_price, 2),
                'low_price': round(low_price, 2),
                'close_price': round(close_price, 2),
                'volume': random.randint(100000, 10000000),
                'adjusted_close': round(close_price, 2),
            })
        
        return data