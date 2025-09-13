"""Backtesting engine services for strategy simulation and analysis.

This module provides comprehensive backtesting functionality including
strategy execution, portfolio simulation, and performance analysis.
"""

import logging
from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, date, timedelta
from dataclasses import dataclass, field

import pandas as pd
import numpy as np
from django.db import transaction
from django.utils import timezone
from django.db.models import Q, F

try:
    from personal_finance.assets.models import Asset
except ImportError:
    Asset = None

# Try to import PriceHistory model if it exists, otherwise use stub
try:
    from personal_finance.assets.models import PriceHistory
except ImportError:
    # PriceHistory doesn't exist in current schema - mock it for now
    class PriceHistoryStubManager:
        """Stub manager for PriceHistory to handle Django ORM operations gracefully."""
        
        def filter(self, **kwargs):
            """Stub filter method that returns empty result."""
            logger.warning("PriceHistory.objects.filter called on stub - implement actual model. Filters: %s", kwargs)
            return self
        
        def order_by(self, *args):
            """Stub order_by method for chaining."""
            return self
        
        def values(self, *args):
            """Stub values method that returns empty list."""
            return []
    
    class PriceHistory:
        """Stub PriceHistory model. Any usage should be replaced with the real model."""
        objects = PriceHistoryStubManager()
from personal_finance.analytics.services import PerformanceAnalytics, TechnicalIndicators
from personal_finance.data_sources.services import data_source_manager
from .models import (
    Strategy, Backtest, BacktestResult, BacktestPortfolioSnapshot,
    BacktestTrade
)

logger = logging.getLogger(__name__)


@dataclass
class Position:
    """Represents a position in the backtesting portfolio."""
    asset: Asset
    quantity: Decimal = field(default_factory=lambda: Decimal('0'))
    average_cost: Decimal = field(default_factory=lambda: Decimal('0'))
    current_price: Decimal = field(default_factory=lambda: Decimal('0'))
    
    @property
    def market_value(self) -> Decimal:
        """Calculate current market value of position."""
        return self.quantity * self.current_price
    
    @property
    def cost_basis(self) -> Decimal:
        """Calculate total cost basis of position."""
        return self.quantity * self.average_cost
    
    @property
    def unrealized_pnl(self) -> Decimal:
        """Calculate unrealized profit/loss."""
        return self.market_value - self.cost_basis
    
    @property
    def unrealized_pnl_percentage(self) -> Decimal:
        """Calculate unrealized P&L as percentage."""
        if self.cost_basis > 0:
            return (self.unrealized_pnl / self.cost_basis) * 100
        return Decimal('0')


@dataclass
class Trade:
    """Represents a trade to be executed."""
    asset: Asset
    quantity: Decimal
    trade_type: str  # 'buy', 'sell', 'short', 'cover'
    signal_strength: Optional[Decimal] = None
    reason: str = ""


@dataclass
class PortfolioState:
    """Represents the current state of the backtesting portfolio."""
    cash: Decimal
    positions: Dict[str, Position] = field(default_factory=dict)
    date: Optional[date] = None
    
    @property
    def total_value(self) -> Decimal:
        """Calculate total portfolio value."""
        position_value = sum(pos.market_value for pos in self.positions.values())
        return self.cash + position_value
    
    @property
    def invested_value(self) -> Decimal:
        """Calculate total invested value."""
        return sum(pos.market_value for pos in self.positions.values())
    
    def get_position(self, symbol: str) -> Position:
        """Get position for symbol, creating empty position if not exists."""
        if symbol not in self.positions:
            asset = Asset.objects.filter(symbol=symbol).first()
            if asset:
                self.positions[symbol] = Position(asset=asset)
        return self.positions.get(symbol, Position(asset=None))


class BaseStrategy(ABC):
    """Abstract base class for trading strategies.
    
    All backtesting strategies must inherit from this class and implement
    the generate_signals method to define their trading logic.
    """
    
    def __init__(self, strategy: Strategy, price_data: pd.DataFrame):
        """Initialize strategy with configuration and data.
        
        Args:
            strategy: Strategy model instance with parameters
            price_data: Historical price data DataFrame
        """
        self.strategy = strategy
        self.price_data = price_data
        self.parameters = strategy.parameters
        self.technical_indicators = TechnicalIndicators()
        
    @abstractmethod
    def generate_signals(self, current_date: date, portfolio: PortfolioState) -> List[Trade]:
        """Generate trading signals for current date.
        
        Args:
            current_date: Current simulation date
            portfolio: Current portfolio state
            
        Returns:
            List of trades to execute
        """
        pass
    
    def get_parameter(self, key: str, default: Any = None) -> Any:
        """Get strategy parameter value."""
        return self.parameters.get(key, default)
    
    def should_rebalance(self, current_date: date, last_rebalance: Optional[date]) -> bool:
        """Check if portfolio should be rebalanced."""
        if last_rebalance is None:
            return True
            
        frequency = self.strategy.rebalance_frequency
        days_since_rebalance = (current_date - last_rebalance).days
        
        if frequency == 'daily':
            return days_since_rebalance >= 1
        elif frequency == 'weekly':
            return days_since_rebalance >= 7
        elif frequency == 'monthly':
            return days_since_rebalance >= 30
        elif frequency == 'quarterly':
            return days_since_rebalance >= 90
        elif frequency == 'yearly':
            return days_since_rebalance >= 365
        
        return False


class BuyAndHoldStrategy(BaseStrategy):
    """Simple buy and hold strategy implementation."""
    
    def generate_signals(self, current_date: date, portfolio: PortfolioState) -> List[Trade]:
        """Generate buy signals for equal-weight portfolio on first day."""
        trades = []
        
        # Only trade on first day
        if portfolio.date is None or len(portfolio.positions) == 0:
            assets = list(self.strategy.asset_universe.all())
            if not assets:
                return trades
                
            # Equal weight allocation
            allocation_per_asset = Decimal('1.0') / len(assets)
            cash_per_asset = portfolio.cash * allocation_per_asset
            
            for asset in assets:
                if asset.symbol in self.price_data.columns:
                    current_price = self.price_data.loc[current_date, asset.symbol] if current_date in self.price_data.index else None
                    if current_price and current_price > 0:
                        quantity = cash_per_asset / Decimal(str(current_price))
                        quantity = quantity.quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
                        
                        if quantity > 0:
                            trades.append(Trade(
                                asset=asset,
                                quantity=quantity,
                                trade_type='buy',
                                reason='Initial buy and hold allocation'
                            ))
        
        return trades


class MovingAverageCrossoverStrategy(BaseStrategy):
    """Moving average crossover strategy implementation."""
    
    def generate_signals(self, current_date: date, portfolio: PortfolioState) -> List[Trade]:
        """Generate signals based on moving average crossovers."""
        trades = []
        
        short_window = self.get_parameter('short_window', 20)
        long_window = self.get_parameter('long_window', 50)
        
        for asset in self.strategy.asset_universe.all():
            if asset.symbol not in self.price_data.columns:
                continue
                
            # Get price history for this asset
            asset_prices = self.price_data[asset.symbol].dropna()
            
            if len(asset_prices) < long_window:
                continue
                
            # Calculate moving averages
            short_ma = asset_prices.rolling(window=short_window).mean()
            long_ma = asset_prices.rolling(window=long_window).mean()
            
            if current_date not in short_ma.index or current_date not in long_ma.index:
                continue
                
            current_short_ma = short_ma.loc[current_date]
            current_long_ma = long_ma.loc[current_date]
            
            # Get previous values for crossover detection
            prev_dates = asset_prices.index[asset_prices.index < current_date]
            if len(prev_dates) == 0:
                continue
                
            prev_date = prev_dates[-1]
            prev_short_ma = short_ma.loc[prev_date] if prev_date in short_ma.index else None
            prev_long_ma = long_ma.loc[prev_date] if prev_date in long_ma.index else None
            
            if prev_short_ma is None or prev_long_ma is None:
                continue
                
            current_position = portfolio.get_position(asset.symbol)
            max_position_value = portfolio.total_value * self.strategy.max_position_size
            current_price = Decimal(str(asset_prices.loc[current_date]))
            
            # Buy signal: short MA crosses above long MA
            if (prev_short_ma <= prev_long_ma and 
                current_short_ma > current_long_ma and 
                current_position.quantity == 0):
                
                quantity = max_position_value / current_price
                quantity = quantity.quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
                
                if quantity > 0 and portfolio.cash >= quantity * current_price:
                    trades.append(Trade(
                        asset=asset,
                        quantity=quantity,
                        trade_type='buy',
                        signal_strength=Decimal('1.0'),
                        reason=f'MA crossover: {short_window}/{long_window}'
                    ))
            
            # Sell signal: short MA crosses below long MA
            elif (prev_short_ma >= prev_long_ma and 
                  current_short_ma < current_long_ma and 
                  current_position.quantity > 0):
                
                trades.append(Trade(
                    asset=asset,
                    quantity=current_position.quantity,
                    trade_type='sell',
                    signal_strength=Decimal('1.0'),
                    reason=f'MA crossover: {short_window}/{long_window}'
                ))
        
        return trades


class RSIStrategy(BaseStrategy):
    """RSI-based mean reversion strategy."""
    
    def generate_signals(self, current_date: date, portfolio: PortfolioState) -> List[Trade]:
        """Generate signals based on RSI levels."""
        trades = []
        
        rsi_period = self.get_parameter('rsi_period', 14)
        oversold_threshold = self.get_parameter('oversold_threshold', 30)
        overbought_threshold = self.get_parameter('overbought_threshold', 70)
        
        for asset in self.strategy.asset_universe.all():
            if asset.symbol not in self.price_data.columns:
                continue
                
            asset_prices = self.price_data[asset.symbol].dropna()
            
            if len(asset_prices) < rsi_period + 1:
                continue
                
            # Calculate RSI
            rsi_values = self.technical_indicators.calculate_rsi(
                asset_prices, period=rsi_period
            )
            
            if current_date not in rsi_values.index:
                continue
                
            current_rsi = rsi_values.loc[current_date]
            current_position = portfolio.get_position(asset.symbol)
            max_position_value = portfolio.total_value * self.strategy.max_position_size
            current_price = Decimal(str(asset_prices.loc[current_date]))
            
            # Buy signal: RSI oversold
            if (current_rsi < oversold_threshold and 
                current_position.quantity == 0):
                
                quantity = max_position_value / current_price
                quantity = quantity.quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
                
                if quantity > 0 and portfolio.cash >= quantity * current_price:
                    signal_strength = Decimal(str((oversold_threshold - current_rsi) / oversold_threshold))
                    trades.append(Trade(
                        asset=asset,
                        quantity=quantity,
                        trade_type='buy',
                        signal_strength=signal_strength,
                        reason=f'RSI oversold: {current_rsi:.1f}'
                    ))
            
            # Sell signal: RSI overbought
            elif (current_rsi > overbought_threshold and 
                  current_position.quantity > 0):
                
                signal_strength = Decimal(str((current_rsi - overbought_threshold) / (100 - overbought_threshold)))
                trades.append(Trade(
                    asset=asset,
                    quantity=current_position.quantity,
                    trade_type='sell',
                    signal_strength=signal_strength,
                    reason=f'RSI overbought: {current_rsi:.1f}'
                ))
        
        return trades


class BacktestEngine:
    """Core backtesting simulation engine.
    
    Executes strategy backtests with realistic trading constraints,
    transaction costs, and portfolio management rules.
    """
    
    def __init__(self):
        """Initialize backtesting engine."""
        self.performance_analytics = PerformanceAnalytics()
        
    def run_backtest(self, backtest: Backtest) -> BacktestResult:
        """Execute a complete backtest simulation.
        
        Args:
            backtest: Backtest configuration to run
            
        Returns:
            Comprehensive backtest results
            
        Raises:
            ValueError: If backtest configuration is invalid
            RuntimeError: If backtest execution fails
        """
        logger.info(f"Starting backtest: {backtest.name}")
        
        try:
            with transaction.atomic():
                # Update backtest status
                backtest.status = 'running'
                backtest.started_at = timezone.now()
                backtest.progress_percentage = 0
                backtest.save()
                
                # Load historical data
                price_data = self._load_price_data(backtest)
                if price_data.empty:
                    raise ValueError("No price data available for backtest period")
                
                # Initialize strategy
                strategy_instance = self._create_strategy_instance(backtest.strategy, price_data)
                
                # Initialize portfolio
                portfolio = PortfolioState(cash=backtest.strategy.initial_capital)
                
                # Run simulation
                simulation_results = self._run_simulation(
                    backtest, strategy_instance, portfolio, price_data
                )
                
                # Calculate performance metrics
                result = self._calculate_results(backtest, simulation_results, price_data)
                
                # Update backtest status
                backtest.status = 'completed'
                backtest.completed_at = timezone.now()
                backtest.progress_percentage = 100
                backtest.save()
                
                logger.info(f"Backtest completed: {backtest.name}")
                return result
                
        except Exception as e:
            logger.error(f"Backtest failed: {backtest.name} - {str(e)}")
            backtest.status = 'failed'
            backtest.error_message = str(e)
            backtest.completed_at = timezone.now()
            backtest.save()
            raise RuntimeError(f"Backtest execution failed: {str(e)}")
    
    def _load_price_data(self, backtest: Backtest) -> pd.DataFrame:
        """Load historical price data for backtest assets."""
        assets = list(backtest.strategy.asset_universe.all())
        if backtest.benchmark_asset:
            assets.append(backtest.benchmark_asset)
        
        price_data = {}
        
        for asset in assets:
            # Get price history from database
            prices = PriceHistory.objects.filter(
                asset=asset,
                date__gte=backtest.start_date,
                date__lte=backtest.end_date
            ).order_by('date').values('date', 'close_price')
            
            if prices:
                asset_prices = pd.Series(
                    [float(p['close_price']) for p in prices],
                    index=[p['date'] for p in prices],
                    name=asset.symbol
                )
                price_data[asset.symbol] = asset_prices
        
        if price_data:
            df = pd.DataFrame(price_data)
            df.index = pd.to_datetime(df.index)
            return df.fillna(method='ffill')  # Forward fill missing values
        
        return pd.DataFrame()
    
    def _create_strategy_instance(self, strategy: Strategy, price_data: pd.DataFrame) -> BaseStrategy:
        """Create strategy instance based on strategy type."""
        strategy_classes = {
            'buy_hold': BuyAndHoldStrategy,
            'moving_average': MovingAverageCrossoverStrategy,
            'rsi': RSIStrategy,
            # Add more strategies here
        }
        
        strategy_class = strategy_classes.get(strategy.strategy_type)
        if not strategy_class:
            raise ValueError(f"Unknown strategy type: {strategy.strategy_type}")
        
        return strategy_class(strategy, price_data)
    
    def _run_simulation(
        self, 
        backtest: Backtest, 
        strategy: BaseStrategy, 
        portfolio: PortfolioState,
        price_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """Run the main simulation loop."""
        
        simulation_results = {
            'daily_values': [],
            'daily_returns': [],
            'trades': [],
            'snapshots': [],
            'benchmark_values': []
        }
        
        trading_dates = price_data.index
        total_days = len(trading_dates)
        last_rebalance_date = None
        
        for i, current_date in enumerate(trading_dates):
            # Update progress
            progress = int((i / total_days) * 100)
            if progress != backtest.progress_percentage:
                backtest.progress_percentage = progress
                backtest.save(update_fields=['progress_percentage'])
            
            # Update portfolio positions with current prices
            self._update_portfolio_prices(portfolio, price_data, current_date)
            portfolio.date = current_date.date()
            
            # Generate trading signals
            if strategy.should_rebalance(current_date.date(), last_rebalance_date):
                trades = strategy.generate_signals(current_date.date(), portfolio)
                
                # Execute trades
                for trade in trades:
                    executed_trade = self._execute_trade(
                        backtest, trade, portfolio, current_date.date()
                    )
                    if executed_trade:
                        simulation_results['trades'].append(executed_trade)
                
                last_rebalance_date = current_date.date()
            
            # Apply stop loss and take profit rules
            self._apply_risk_management(backtest, portfolio, current_date.date(), simulation_results)
            
            # Record daily portfolio snapshot
            snapshot = self._create_portfolio_snapshot(
                backtest, portfolio, current_date.date(), price_data
            )
            simulation_results['snapshots'].append(snapshot)
            simulation_results['daily_values'].append(float(portfolio.total_value))
            
            # Calculate daily return
            if len(simulation_results['daily_values']) > 1:
                prev_value = simulation_results['daily_values'][-2]
                current_value = simulation_results['daily_values'][-1]
                daily_return = (current_value - prev_value) / prev_value if prev_value > 0 else 0
                simulation_results['daily_returns'].append(daily_return)
            else:
                simulation_results['daily_returns'].append(0.0)
            
            # Calculate benchmark value if available
            if backtest.benchmark_asset and backtest.benchmark_asset.symbol in price_data.columns:
                benchmark_price = price_data.loc[current_date, backtest.benchmark_asset.symbol]
                if i == 0:
                    initial_benchmark_price = benchmark_price
                    benchmark_value = float(backtest.strategy.initial_capital)
                else:
                    benchmark_value = float(backtest.strategy.initial_capital) * (benchmark_price / initial_benchmark_price)
                simulation_results['benchmark_values'].append(benchmark_value)
        
        return simulation_results
    
    def _update_portfolio_prices(
        self, 
        portfolio: PortfolioState, 
        price_data: pd.DataFrame, 
        current_date: pd.Timestamp
    ) -> None:
        """Update current prices for all portfolio positions."""
        for symbol, position in portfolio.positions.items():
            if symbol in price_data.columns and current_date in price_data.index:
                current_price = price_data.loc[current_date, symbol]
                position.current_price = Decimal(str(current_price))
    
    def _execute_trade(
        self, 
        backtest: Backtest, 
        trade: Trade, 
        portfolio: PortfolioState,
        trade_date: date
    ) -> Optional[BacktestTrade]:
        """Execute a trade with realistic constraints and costs."""
        
        position = portfolio.get_position(trade.asset.symbol)
        trade_value = trade.quantity * position.current_price
        
        # Calculate transaction costs
        transaction_cost = trade_value * backtest.transaction_costs
        slippage_cost = trade_value * backtest.slippage
        total_cost = transaction_cost + slippage_cost
        
        portfolio_value_before = portfolio.total_value
        
        if trade.trade_type == 'buy':
            total_required = trade_value + total_cost
            if portfolio.cash >= total_required:
                # Update position
                total_quantity = position.quantity + trade.quantity
                total_cost_basis = (position.quantity * position.average_cost) + trade_value
                position.average_cost = total_cost_basis / total_quantity if total_quantity > 0 else Decimal('0')
                position.quantity = total_quantity
                
                # Update cash
                portfolio.cash -= total_required
                
                # Create trade record
                trade_record = BacktestTrade.objects.create(
                    backtest=backtest,
                    asset=trade.asset,
                    trade_type='buy',
                    date=trade_date,
                    quantity=trade.quantity,
                    price=position.current_price,
                    transaction_cost=transaction_cost,
                    slippage_cost=slippage_cost,
                    gross_value=trade_value,
                    net_value=trade_value + total_cost,
                    signal_strength=trade.signal_strength,
                    reason=trade.reason,
                    portfolio_value_before=portfolio_value_before,
                    portfolio_value_after=portfolio.total_value,
                    position_size_percentage=(trade_value / portfolio_value_before) * 100 if portfolio_value_before > 0 else Decimal('0')
                )
                
                return trade_record
                
        elif trade.trade_type == 'sell':
            if position.quantity >= trade.quantity:
                # Update position
                position.quantity -= trade.quantity
                if position.quantity == 0:
                    position.average_cost = Decimal('0')
                
                # Update cash (subtract costs from proceeds)
                proceeds = trade_value - total_cost
                portfolio.cash += proceeds
                
                # Create trade record
                trade_record = BacktestTrade.objects.create(
                    backtest=backtest,
                    asset=trade.asset,
                    trade_type='sell',
                    date=trade_date,
                    quantity=trade.quantity,
                    price=position.current_price,
                    transaction_cost=transaction_cost,
                    slippage_cost=slippage_cost,
                    gross_value=trade_value,
                    net_value=proceeds,
                    signal_strength=trade.signal_strength,
                    reason=trade.reason,
                    portfolio_value_before=portfolio_value_before,
                    portfolio_value_after=portfolio.total_value,
                    position_size_percentage=(trade_value / portfolio_value_before) * 100 if portfolio_value_before > 0 else Decimal('0')
                )
                
                return trade_record
        
        return None
    
    def _apply_risk_management(
        self, 
        backtest: Backtest, 
        portfolio: PortfolioState,
        current_date: date,
        simulation_results: Dict[str, Any]
    ) -> None:
        """Apply stop loss and take profit rules."""
        
        strategy = backtest.strategy
        if not strategy.stop_loss_percentage and not strategy.take_profit_percentage:
            return
            
        for symbol, position in portfolio.positions.items():
            if position.quantity <= 0:
                continue
                
            unrealized_pnl_pct = position.unrealized_pnl_percentage / 100  # Convert to decimal
            
            # Stop loss check
            if (strategy.stop_loss_percentage and 
                unrealized_pnl_pct <= -strategy.stop_loss_percentage):
                
                stop_loss_trade = Trade(
                    asset=position.asset,
                    quantity=position.quantity,
                    trade_type='sell',
                    reason=f'Stop loss: {unrealized_pnl_pct:.2%}'
                )
                
                executed_trade = self._execute_trade(
                    backtest, stop_loss_trade, portfolio, current_date
                )
                if executed_trade:
                    simulation_results['trades'].append(executed_trade)
            
            # Take profit check
            elif (strategy.take_profit_percentage and 
                  unrealized_pnl_pct >= strategy.take_profit_percentage):
                
                take_profit_trade = Trade(
                    asset=position.asset,
                    quantity=position.quantity,
                    trade_type='sell',
                    reason=f'Take profit: {unrealized_pnl_pct:.2%}'
                )
                
                executed_trade = self._execute_trade(
                    backtest, take_profit_trade, portfolio, current_date
                )
                if executed_trade:
                    simulation_results['trades'].append(executed_trade)
    
    def _create_portfolio_snapshot(
        self,
        backtest: Backtest,
        portfolio: PortfolioState,
        snapshot_date: date,
        price_data: pd.DataFrame
    ) -> BacktestPortfolioSnapshot:
        """Create a portfolio snapshot for the current date."""
        
        # Calculate benchmark value if available
        benchmark_value = None
        benchmark_return = None
        
        if backtest.benchmark_asset and backtest.benchmark_asset.symbol in price_data.columns:
            current_date = pd.Timestamp(snapshot_date)
            if current_date in price_data.index:
                current_benchmark_price = price_data.loc[current_date, backtest.benchmark_asset.symbol]
                first_date = price_data.index[0]
                initial_benchmark_price = price_data.loc[first_date, backtest.benchmark_asset.symbol]
                
                benchmark_value = float(backtest.strategy.initial_capital) * (current_benchmark_price / initial_benchmark_price)
                benchmark_return = (benchmark_value / float(backtest.strategy.initial_capital) - 1) * 100
        
        # Calculate cumulative return
        cumulative_return = (float(portfolio.total_value) / float(backtest.strategy.initial_capital) - 1) * 100
        
        # Prepare positions data
        positions_data = {}
        for symbol, position in portfolio.positions.items():
            if position.quantity > 0:
                weight = (float(position.market_value) / float(portfolio.total_value)) * 100 if portfolio.total_value > 0 else 0
                positions_data[symbol] = {
                    'quantity': float(position.quantity),
                    'value': float(position.market_value),
                    'weight': weight,
                    'average_cost': float(position.average_cost),
                    'current_price': float(position.current_price),
                    'unrealized_pnl': float(position.unrealized_pnl),
                    'unrealized_pnl_pct': float(position.unrealized_pnl_percentage)
                }
        
        snapshot = BacktestPortfolioSnapshot.objects.create(
            backtest=backtest,
            date=snapshot_date,
            total_value=portfolio.total_value,
            cash_balance=portfolio.cash,
            invested_value=portfolio.invested_value,
            cumulative_return=Decimal(str(cumulative_return)),
            positions=positions_data,
            benchmark_value=Decimal(str(benchmark_value)) if benchmark_value else None,
            benchmark_return=Decimal(str(benchmark_return)) if benchmark_return else None
        )
        
        return snapshot
    
    def _calculate_results(
        self,
        backtest: Backtest,
        simulation_results: Dict[str, Any],
        price_data: pd.DataFrame
    ) -> BacktestResult:
        """Calculate comprehensive backtest performance results."""
        
        daily_values = simulation_results['daily_values']
        daily_returns = simulation_results['daily_returns']
        trades = simulation_results['trades']
        benchmark_values = simulation_results['benchmark_values']
        
        # Basic performance metrics
        initial_value = float(backtest.strategy.initial_capital)
        final_value = daily_values[-1] if daily_values else initial_value
        total_return = (final_value / initial_value - 1) * 100
        
        # Calculate annualized return
        days = (backtest.end_date - backtest.start_date).days
        years = days / 365.25
        annualized_return = ((final_value / initial_value) ** (1 / years) - 1) * 100 if years > 0 else 0
        
        # Calculate volatility (annualized)
        returns_series = pd.Series(daily_returns)
        volatility = returns_series.std() * np.sqrt(252) * 100  # Annualized
        
        # Risk metrics
        sharpe_ratio = None
        if volatility > 0:
            excess_return = annualized_return - (self.performance_analytics.risk_free_rate * 100)
            sharpe_ratio = excess_return / volatility
        
        # Maximum drawdown
        portfolio_values = pd.Series(daily_values)
        rolling_max = portfolio_values.expanding().max()
        drawdowns = (portfolio_values - rolling_max) / rolling_max
        max_drawdown = abs(drawdowns.min()) * 100
        
        # Value at Risk (95%)
        var_95 = None
        if len(daily_returns) > 0:
            var_95 = np.percentile(daily_returns, 5) * 100
        
        # Calmar ratio
        calmar_ratio = None
        if max_drawdown > 0:
            calmar_ratio = annualized_return / max_drawdown
        
        # Trading statistics
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t.trade_type == 'sell' and self._calculate_trade_pnl(t, trades) > 0])
        losing_trades = total_trades - winning_trades
        win_rate = (winning_trades / total_trades) if total_trades > 0 else 0
        
        # Calculate average win/loss
        trade_returns = []
        for trade in trades:
            if trade.trade_type == 'sell':
                pnl = self._calculate_trade_pnl(trade, trades)
                trade_returns.append(pnl)
        
        winning_returns = [r for r in trade_returns if r > 0]
        losing_returns = [r for r in trade_returns if r < 0]
        
        average_win = np.mean(winning_returns) * 100 if winning_returns else None
        average_loss = np.mean(losing_returns) * 100 if losing_returns else None
        
        # Benchmark comparison
        benchmark_return = None
        alpha = None
        beta = None
        information_ratio = None
        
        if benchmark_values:
            benchmark_final = benchmark_values[-1]
            benchmark_return = (benchmark_final / initial_value - 1) * 100
            
            # Calculate alpha, beta, information ratio
            strategy_returns = pd.Series(daily_returns)
            benchmark_daily_returns = []
            for i in range(1, len(benchmark_values)):
                ret = (benchmark_values[i] - benchmark_values[i-1]) / benchmark_values[i-1]
                benchmark_daily_returns.append(ret)
            
            if benchmark_daily_returns:
                benchmark_series = pd.Series(benchmark_daily_returns)
                
                # Beta calculation
                covariance = np.cov(strategy_returns[1:], benchmark_series)[0][1]
                benchmark_variance = np.var(benchmark_series)
                beta = covariance / benchmark_variance if benchmark_variance > 0 else None
                
                # Alpha calculation (annualized)
                if beta is not None:
                    alpha = annualized_return - (self.performance_analytics.risk_free_rate * 100 + beta * (np.mean(benchmark_series) * 252 * 100))
                
                # Information ratio
                excess_returns = strategy_returns[1:] - benchmark_series
                tracking_error = excess_returns.std() * np.sqrt(252)
                if tracking_error > 0:
                    information_ratio = (annualized_return - (np.mean(benchmark_series) * 252 * 100)) / (tracking_error * 100)
        
        # Total transaction costs
        total_transaction_costs = sum(float(trade.transaction_cost + trade.slippage_cost) for trade in trades)
        
        # Create result object
        result = BacktestResult.objects.create(
            backtest=backtest,
            total_return=Decimal(str(total_return)),
            annualized_return=Decimal(str(annualized_return)),
            volatility=Decimal(str(volatility)),
            sharpe_ratio=Decimal(str(sharpe_ratio)) if sharpe_ratio else None,
            max_drawdown=Decimal(str(max_drawdown)),
            var_95=Decimal(str(var_95)) if var_95 else None,
            calmar_ratio=Decimal(str(calmar_ratio)) if calmar_ratio else None,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=Decimal(str(win_rate)),
            average_win=Decimal(str(average_win)) if average_win else None,
            average_loss=Decimal(str(average_loss)) if average_loss else None,
            benchmark_return=Decimal(str(benchmark_return)) if benchmark_return else None,
            alpha=Decimal(str(alpha)) if alpha else None,
            beta=Decimal(str(beta)) if beta else None,
            information_ratio=Decimal(str(information_ratio)) if information_ratio else None,
            final_portfolio_value=Decimal(str(final_value)),
            cash_balance=simulation_results['snapshots'][-1].cash_balance if simulation_results['snapshots'] else Decimal('0'),
            total_transaction_costs=Decimal(str(total_transaction_costs)),
            daily_returns=daily_returns,
            portfolio_values=daily_values,
            positions_history=[],  # Could be populated with detailed position history
            trade_history=[self._serialize_trade(trade) for trade in trades]
        )
        
        return result
    
    def _calculate_trade_pnl(self, sell_trade: BacktestTrade, all_trades: List[BacktestTrade]) -> float:
        """Calculate profit/loss for a completed trade."""
        # This is a simplified calculation - in reality you'd match specific buy/sell pairs
        # For now, just use the trade's portfolio impact
        return float(sell_trade.portfolio_value_after - sell_trade.portfolio_value_before)
    
    def _serialize_trade(self, trade: BacktestTrade) -> Dict[str, Any]:
        """Serialize trade for JSON storage."""
        return {
            'date': trade.date.isoformat(),
            'asset': trade.asset.symbol,
            'type': trade.trade_type,
            'quantity': float(trade.quantity),
            'price': float(trade.price),
            'value': float(trade.gross_value),
            'cost': float(trade.transaction_cost + trade.slippage_cost),
            'reason': trade.reason,
            'signal_strength': float(trade.signal_strength) if trade.signal_strength else None
        }


# Strategy registry for easy access
STRATEGY_REGISTRY = {
    'buy_hold': BuyAndHoldStrategy,
    'moving_average': MovingAverageCrossoverStrategy,
    'rsi': RSIStrategy,
}


def get_available_strategies() -> List[Tuple[str, str]]:
    """Get list of available strategy types."""
    return [
        ('buy_hold', 'Buy and Hold'),
        ('moving_average', 'Moving Average Crossover'),
        ('rsi', 'RSI Strategy'),
    ]


# Convenience functions
def create_strategy(
    user,
    name: str,
    strategy_type: str,
    parameters: Dict[str, Any],
    asset_symbols: List[str],
    **kwargs
) -> Strategy:
    """Create a new strategy with specified parameters."""
    
    strategy = Strategy.objects.create(
        user=user,
        name=name,
        strategy_type=strategy_type,
        parameters=parameters,
        **kwargs
    )
    
    # Add assets to universe
    assets = Asset.objects.filter(symbol__in=asset_symbols)
    strategy.asset_universe.add(*assets)
    
    return strategy


def run_quick_backtest(
    strategy: Strategy,
    start_date: date,
    end_date: date,
    benchmark_symbol: Optional[str] = None
) -> BacktestResult:
    """Run a quick backtest with default parameters."""
    
    benchmark_asset = None
    if benchmark_symbol:
        benchmark_asset = Asset.objects.filter(symbol=benchmark_symbol).first()
    
    backtest = Backtest.objects.create(
        strategy=strategy,
        name=f"Quick Backtest - {strategy.name}",
        start_date=start_date,
        end_date=end_date,
        benchmark_asset=benchmark_asset
    )
    
    engine = BacktestEngine()
    return engine.run_backtest(backtest)