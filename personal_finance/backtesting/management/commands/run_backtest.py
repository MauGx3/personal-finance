"""Management command to run backtests from the command line.

This command allows running backtests programmatically, useful for
scheduled backtesting, batch processing, and automated testing.
"""

import logging
from decimal import Decimal
from datetime import datetime, date, timedelta
from typing import Optional, List

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone

from personal_finance.assets.models import Asset
from personal_finance.backtesting.models import Strategy, Backtest
from personal_finance.backtesting.services import BacktestEngine, create_strategy

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Management command for running backtests."""
    
    help = 'Run backtests for specified strategies or create and run new strategies'
    
    def add_arguments(self, parser):
        """Add command line arguments."""
        
        # Backtest selection
        parser.add_argument(
            '--backtest-id',
            type=int,
            help='Specific backtest ID to run'
        )
        parser.add_argument(
            '--strategy-id',
            type=int,
            help='Strategy ID to create new backtest for'
        )
        parser.add_argument(
            '--strategy-name',
            type=str,
            help='Strategy name to create new backtest for'
        )
        parser.add_argument(
            '--all-pending',
            action='store_true',
            help='Run all pending backtests'
        )
        
        # Time period for new backtests
        parser.add_argument(
            '--start-date',
            type=str,
            help='Start date for new backtest (YYYY-MM-DD)'
        )
        parser.add_argument(
            '--end-date',
            type=str,
            help='End date for new backtest (YYYY-MM-DD)'
        )
        parser.add_argument(
            '--period',
            type=str,
            choices=['1y', '2y', '3y', '5y', '10y'],
            default='2y',
            help='Predefined backtest period (default: 2y)'
        )
        
        # Quick strategy creation
        parser.add_argument(
            '--create-strategy',
            type=str,
            choices=['buy_hold', 'moving_average', 'rsi'],
            help='Create a new strategy of specified type'
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Username for new strategy (required with --create-strategy)'
        )
        parser.add_argument(
            '--assets',
            type=str,
            nargs='+',
            help='Asset symbols for new strategy (e.g., AAPL MSFT GOOGL)'
        )
        parser.add_argument(
            '--benchmark',
            type=str,
            default='SPY',
            help='Benchmark symbol (default: SPY)'
        )
        
        # Strategy parameters
        parser.add_argument(
            '--initial-capital',
            type=float,
            default=100000.0,
            help='Initial capital for new strategy (default: 100000)'
        )
        parser.add_argument(
            '--max-position-size',
            type=float,
            default=0.1,
            help='Maximum position size as decimal (default: 0.1 = 10%%)'
        )
        
        # Moving average parameters
        parser.add_argument(
            '--short-window',
            type=int,
            default=20,
            help='Short moving average window for MA strategy (default: 20)'
        )
        parser.add_argument(
            '--long-window',
            type=int,
            default=50,
            help='Long moving average window for MA strategy (default: 50)'
        )
        
        # RSI parameters
        parser.add_argument(
            '--rsi-period',
            type=int,
            default=14,
            help='RSI period for RSI strategy (default: 14)'
        )
        parser.add_argument(
            '--oversold-threshold',
            type=int,
            default=30,
            help='RSI oversold threshold (default: 30)'
        )
        parser.add_argument(
            '--overbought-threshold',
            type=int,
            default=70,
            help='RSI overbought threshold (default: 70)'
        )
        
        # Execution options
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without executing'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output'
        )
    
    def handle(self, *args, **options):
        """Execute the command."""
        
        # Configure logging
        if options['verbose']:
            logging.basicConfig(level=logging.INFO)
        
        try:
            if options['create_strategy']:
                self._create_and_run_strategy(options)
            elif options['backtest_id']:
                self._run_specific_backtest(options['backtest_id'], options)
            elif options['strategy_id'] or options['strategy_name']:
                self._create_backtest_for_strategy(options)
            elif options['all_pending']:
                self._run_all_pending_backtests(options)
            else:
                raise CommandError(
                    "Must specify one of: --backtest-id, --strategy-id, "
                    "--strategy-name, --create-strategy, or --all-pending"
                )
                
        except Exception as e:
            logger.error(f"Command failed: {str(e)}")
            raise CommandError(f"Command execution failed: {str(e)}")
    
    def _create_and_run_strategy(self, options):
        """Create a new strategy and run backtest."""
        
        if not options['user']:
            raise CommandError("--user is required when creating a strategy")
        
        if not options['assets']:
            raise CommandError("--assets is required when creating a strategy")
        
        # Get user
        try:
            user = User.objects.get(username=options['user'])
        except User.DoesNotExist:
            raise CommandError(f"User '{options['user']}' not found")
        
        # Validate assets
        asset_symbols = options['assets']
        existing_assets = Asset.objects.filter(symbol__in=asset_symbols)
        existing_symbols = set(existing_assets.values_list('symbol', flat=True))
        missing_symbols = set(asset_symbols) - existing_symbols
        
        if missing_symbols:
            self.stdout.write(
                self.style.WARNING(
                    f"Warning: Assets not found: {', '.join(missing_symbols)}"
                )
            )
            asset_symbols = list(existing_symbols)
        
        if not asset_symbols:
            raise CommandError("No valid assets found")
        
        # Build strategy parameters
        strategy_type = options['create_strategy']
        strategy_name = f"{strategy_type.title()} Strategy - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        parameters = {}
        if strategy_type == 'moving_average':
            parameters = {
                'short_window': options['short_window'],
                'long_window': options['long_window']
            }
        elif strategy_type == 'rsi':
            parameters = {
                'rsi_period': options['rsi_period'],
                'oversold_threshold': options['oversold_threshold'],
                'overbought_threshold': options['overbought_threshold']
            }
        
        if options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Would create strategy: {strategy_name}\n"
                    f"Type: {strategy_type}\n"
                    f"Assets: {', '.join(asset_symbols)}\n"
                    f"Parameters: {parameters}\n"
                    f"Initial Capital: ${options['initial_capital']:,.2f}"
                )
            )
            return
        
        # Create strategy
        strategy = create_strategy(
            user=user,
            name=strategy_name,
            strategy_type=strategy_type,
            parameters=parameters,
            asset_symbols=asset_symbols,
            initial_capital=Decimal(str(options['initial_capital'])),
            max_position_size=Decimal(str(options['max_position_size']))
        )
        
        self.stdout.write(
            self.style.SUCCESS(f"Created strategy: {strategy.name} (ID: {strategy.id})")
        )
        
        # Create and run backtest
        self._create_and_run_backtest_for_strategy(strategy, options)
    
    def _run_specific_backtest(self, backtest_id: int, options):
        """Run a specific backtest by ID."""
        
        try:
            backtest = Backtest.objects.get(id=backtest_id)
        except Backtest.DoesNotExist:
            raise CommandError(f"Backtest with ID {backtest_id} not found")
        
        if backtest.status in ['completed', 'running']:
            if not options.get('force'):
                self.stdout.write(
                    self.style.WARNING(
                        f"Backtest {backtest.name} is already {backtest.status}. "
                        "Use --force to run anyway."
                    )
                )
                return
        
        if options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS(f"Would run backtest: {backtest.name}")
            )
            return
        
        self._execute_backtest(backtest)
    
    def _create_backtest_for_strategy(self, options):
        """Create new backtest for existing strategy."""
        
        # Get strategy
        strategy = None
        if options['strategy_id']:
            try:
                strategy = Strategy.objects.get(id=options['strategy_id'])
            except Strategy.DoesNotExist:
                raise CommandError(f"Strategy with ID {options['strategy_id']} not found")
        elif options['strategy_name']:
            try:
                strategy = Strategy.objects.get(name=options['strategy_name'])
            except Strategy.DoesNotExist:
                raise CommandError(f"Strategy '{options['strategy_name']}' not found")
            except Strategy.MultipleObjectsReturned:
                strategies = Strategy.objects.filter(name=options['strategy_name'])
                raise CommandError(
                    f"Multiple strategies found with name '{options['strategy_name']}'. "
                    f"Use --strategy-id instead. IDs: {list(strategies.values_list('id', flat=True))}"
                )
        
        self._create_and_run_backtest_for_strategy(strategy, options)
    
    def _create_and_run_backtest_for_strategy(self, strategy: Strategy, options):
        """Create and run backtest for a strategy."""
        
        # Calculate dates
        start_date, end_date = self._calculate_dates(options)
        
        # Get benchmark asset
        benchmark_asset = None
        if options.get('benchmark'):
            try:
                benchmark_asset = Asset.objects.get(symbol=options['benchmark'])
            except Asset.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"Benchmark asset '{options['benchmark']}' not found")
                )
        
        # Create backtest
        backtest_name = f"{strategy.name} - {start_date} to {end_date}"
        
        if options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Would create backtest: {backtest_name}\n"
                    f"Period: {start_date} to {end_date}\n"
                    f"Benchmark: {benchmark_asset.symbol if benchmark_asset else 'None'}"
                )
            )
            return
        
        backtest = Backtest.objects.create(
            strategy=strategy,
            name=backtest_name,
            start_date=start_date,
            end_date=end_date,
            benchmark_asset=benchmark_asset
        )
        
        self.stdout.write(
            self.style.SUCCESS(f"Created backtest: {backtest.name} (ID: {backtest.id})")
        )
        
        # Run backtest
        self._execute_backtest(backtest)
    
    def _run_all_pending_backtests(self, options):
        """Run all pending backtests."""
        
        pending_backtests = Backtest.objects.filter(status='pending')
        
        if not pending_backtests.exists():
            self.stdout.write(self.style.SUCCESS("No pending backtests found"))
            return
        
        self.stdout.write(
            self.style.SUCCESS(f"Found {pending_backtests.count()} pending backtests")
        )
        
        if options['dry_run']:
            for backtest in pending_backtests:
                self.stdout.write(f"Would run: {backtest.name}")
            return
        
        for backtest in pending_backtests:
            try:
                self._execute_backtest(backtest)
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to run {backtest.name}: {str(e)}")
                )
    
    def _execute_backtest(self, backtest: Backtest):
        """Execute a backtest and display results."""
        
        self.stdout.write(f"Running backtest: {backtest.name}")
        
        # Check if strategy has assets
        if not backtest.strategy.asset_universe.exists():
            raise CommandError(
                f"Strategy '{backtest.strategy.name}' has no assets in universe"
            )
        
        start_time = timezone.now()
        
        try:
            engine = BacktestEngine()
            result = engine.run_backtest(backtest)
            
            execution_time = (timezone.now() - start_time).total_seconds()
            
            # Display results
            self.stdout.write(self.style.SUCCESS(f"Backtest completed in {execution_time:.1f}s"))
            self.stdout.write(f"")
            self.stdout.write(f"Performance Results:")
            self.stdout.write(f"  Total Return: {result.total_return:.2f}%")
            self.stdout.write(f"  Annualized Return: {result.annualized_return:.2f}%")
            self.stdout.write(f"  Volatility: {result.volatility:.2f}%")
            self.stdout.write(f"  Sharpe Ratio: {result.sharpe_ratio:.2f}" if result.sharpe_ratio else "  Sharpe Ratio: N/A")
            self.stdout.write(f"  Max Drawdown: {result.max_drawdown:.2f}%")
            self.stdout.write(f"")
            self.stdout.write(f"Trading Statistics:")
            self.stdout.write(f"  Total Trades: {result.total_trades}")
            self.stdout.write(f"  Win Rate: {result.win_rate*100:.1f}%" if result.win_rate else "  Win Rate: N/A")
            self.stdout.write(f"  Final Portfolio Value: ${result.final_portfolio_value:,.2f}")
            
            if result.benchmark_return:
                self.stdout.write(f"")
                self.stdout.write(f"Benchmark Comparison:")
                self.stdout.write(f"  Benchmark Return: {result.benchmark_return:.2f}%")
                self.stdout.write(f"  Alpha: {result.alpha:.2f}%" if result.alpha else "  Alpha: N/A")
                self.stdout.write(f"  Beta: {result.beta:.2f}" if result.beta else "  Beta: N/A")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Backtest failed: {str(e)}")
            )
            raise
    
    def _calculate_dates(self, options) -> tuple[date, date]:
        """Calculate start and end dates for backtest."""
        
        if options.get('start_date') and options.get('end_date'):
            start_date = datetime.strptime(options['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(options['end_date'], '%Y-%m-%d').date()
        else:
            # Use period
            end_date = date.today()
            period = options.get('period', '2y')
            
            if period == '1y':
                start_date = end_date - timedelta(days=365)
            elif period == '2y':
                start_date = end_date - timedelta(days=365*2)
            elif period == '3y':
                start_date = end_date - timedelta(days=365*3)
            elif period == '5y':
                start_date = end_date - timedelta(days=365*5)
            elif period == '10y':
                start_date = end_date - timedelta(days=365*10)
            else:
                raise CommandError(f"Invalid period: {period}")
        
        if start_date >= end_date:
            raise CommandError("Start date must be before end date")
        
        return start_date, end_date