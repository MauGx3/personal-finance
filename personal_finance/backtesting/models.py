"""Backtesting models for strategy testing and simulation.

This module provides comprehensive models for backtesting trading strategies,
including strategy definitions, backtest runs, and performance results.
"""

from decimal import Decimal
from typing import Dict, Any, Optional
from datetime import datetime, date

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.postgres.fields import JSONField

from personal_finance.assets.models import Asset

# Graceful import handling for missing models
try:
    from personal_finance.portfolios.models import Portfolio
except ImportError:
    Portfolio = None

User = get_user_model()


class Strategy(models.Model):
    """Trading strategy definition for backtesting.
    
    Defines the parameters and logic for a trading strategy that can be
    backtested against historical data to evaluate performance.
    """
    
    STRATEGY_TYPES = [
        ('buy_hold', 'Buy and Hold'),
        ('moving_average', 'Moving Average Crossover'),
        ('momentum', 'Momentum Strategy'),
        ('mean_reversion', 'Mean Reversion'),
        ('rsi', 'RSI Strategy'),
        ('bollinger', 'Bollinger Bands'),
        ('custom', 'Custom Strategy'),
    ]
    
    REBALANCE_FREQUENCIES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    # Basic Information
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='strategies',
        help_text="User who owns this strategy"
    )
    name = models.CharField(
        max_length=200,
        help_text="Strategy name"
    )
    description = models.TextField(
        blank=True,
        help_text="Strategy description and logic"
    )
    strategy_type = models.CharField(
        max_length=50,
        choices=STRATEGY_TYPES,
        default='buy_hold',
        help_text="Type of trading strategy"
    )
    
    # Strategy Parameters
    parameters = JSONField(
        default=dict,
        help_text="Strategy-specific parameters as JSON"
    )
    
    # Portfolio Management
    initial_capital = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=Decimal('100000.00'),
        validators=[MinValueValidator(Decimal('1000.00'))],
        help_text="Initial capital for backtesting"
    )
    rebalance_frequency = models.CharField(
        max_length=20,
        choices=REBALANCE_FREQUENCIES,
        default='monthly',
        help_text="Portfolio rebalancing frequency"
    )
    
    # Risk Management
    max_position_size = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=Decimal('0.1000'),
        validators=[
            MinValueValidator(Decimal('0.0001')),
            MaxValueValidator(Decimal('1.0000'))
        ],
        help_text="Maximum position size as percentage of portfolio"
    )
    stop_loss_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal('0.0100')),
            MaxValueValidator(Decimal('0.5000'))
        ],
        help_text="Stop loss percentage (optional)"
    )
    take_profit_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal('0.0100')),
            MaxValueValidator(Decimal('5.0000'))
        ],
        help_text="Take profit percentage (optional)"
    )
    
    # Asset Universe
    asset_universe = models.ManyToManyField(
        Asset,
        related_name='strategies',
        help_text="Assets this strategy can trade"
    )
    
    # Metadata
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this strategy is active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Strategies"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'],
                name='unique_user_strategy_name'
            )
        ]
    
    def __str__(self):
        return f"{self.name} ({self.strategy_type})"
    
    def get_parameter(self, key: str, default: Any = None) -> Any:
        """Get strategy parameter value.
        
        Args:
            key: Parameter key
            default: Default value if key not found
            
        Returns:
            Parameter value or default
        """
        return self.parameters.get(key, default)
    
    def set_parameter(self, key: str, value: Any) -> None:
        """Set strategy parameter value.
        
        Args:
            key: Parameter key
            value: Parameter value
        """
        self.parameters[key] = value


class Backtest(models.Model):
    """Backtest run configuration and metadata.
    
    Represents a single backtest run of a strategy against historical data,
    including the time period, benchmark, and execution parameters.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Basic Information
    strategy = models.ForeignKey(
        Strategy,
        on_delete=models.CASCADE,
        related_name='backtests',
        help_text="Strategy being backtested"
    )
    name = models.CharField(
        max_length=200,
        help_text="Backtest run name"
    )
    description = models.TextField(
        blank=True,
        help_text="Backtest description and notes"
    )
    
    # Time Period
    start_date = models.DateField(
        help_text="Backtest start date"
    )
    end_date = models.DateField(
        help_text="Backtest end date"
    )
    
    # Benchmark
    benchmark_asset = models.ForeignKey(
        Asset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='benchmark_backtests',
        help_text="Benchmark asset for comparison (e.g., SPY for S&P 500)"
    )
    
    # Execution Parameters
    transaction_costs = models.DecimalField(
        max_digits=6,
        decimal_places=6,
        default=Decimal('0.001000'),
        validators=[
            MinValueValidator(Decimal('0.000000')),
            MaxValueValidator(Decimal('0.100000'))
        ],
        help_text="Transaction costs as percentage of trade value"
    )
    slippage = models.DecimalField(
        max_digits=6,
        decimal_places=6,
        default=Decimal('0.000500'),
        validators=[
            MinValueValidator(Decimal('0.000000')),
            MaxValueValidator(Decimal('0.050000'))
        ],
        help_text="Market impact slippage as percentage"
    )
    
    # Status and Results
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Backtest execution status"
    )
    progress_percentage = models.IntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        help_text="Backtest completion percentage"
    )
    error_message = models.TextField(
        blank=True,
        help_text="Error message if backtest failed"
    )
    
    # Timing
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When backtest execution started"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When backtest execution completed"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F('start_date')),
                name='backtest_valid_date_range'
            )
        ]
    
    def __str__(self):
        return f"{self.name} - {self.strategy.name}"
    
    @property
    def duration_days(self) -> int:
        """Calculate backtest duration in days."""
        return (self.end_date - self.start_date).days
    
    @property
    def execution_time(self) -> Optional[float]:
        """Calculate execution time in seconds."""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return delta.total_seconds()
        return None
    
    def is_completed(self) -> bool:
        """Check if backtest is completed successfully."""
        return self.status == 'completed'
    
    def is_running(self) -> bool:
        """Check if backtest is currently running."""
        return self.status == 'running'


class BacktestResult(models.Model):
    """Comprehensive backtest performance results and metrics.
    
    Stores detailed performance analysis results from a completed backtest,
    including returns, risk metrics, and benchmark comparisons.
    """
    
    backtest = models.OneToOneField(
        Backtest,
        on_delete=models.CASCADE,
        related_name='result',
        help_text="Associated backtest run"
    )
    
    # Performance Metrics
    total_return = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        help_text="Total return over backtest period"
    )
    annualized_return = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        help_text="Annualized return percentage"
    )
    volatility = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        help_text="Annualized volatility percentage"
    )
    sharpe_ratio = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        help_text="Risk-adjusted return metric"
    )
    
    # Risk Metrics
    max_drawdown = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        help_text="Maximum peak-to-trough decline"
    )
    var_95 = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        help_text="95% Value at Risk"
    )
    calmar_ratio = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        help_text="Calmar ratio (return/max drawdown)"
    )
    
    # Trading Statistics
    total_trades = models.IntegerField(
        default=0,
        help_text="Total number of trades executed"
    )
    winning_trades = models.IntegerField(
        default=0,
        help_text="Number of profitable trades"
    )
    losing_trades = models.IntegerField(
        default=0,
        help_text="Number of losing trades"
    )
    win_rate = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        help_text="Percentage of winning trades"
    )
    average_win = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        help_text="Average winning trade return"
    )
    average_loss = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        help_text="Average losing trade return"
    )
    
    # Benchmark Comparison
    benchmark_return = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        help_text="Benchmark total return"
    )
    alpha = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        help_text="Alpha relative to benchmark"
    )
    beta = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        help_text="Beta relative to benchmark"
    )
    information_ratio = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        help_text="Information ratio vs benchmark"
    )
    
    # Portfolio Statistics
    final_portfolio_value = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        help_text="Final portfolio value"
    )
    cash_balance = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        help_text="Final cash balance"
    )
    total_transaction_costs = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Total transaction costs paid"
    )
    
    # Detailed Results
    daily_returns = JSONField(
        default=list,
        help_text="Daily portfolio returns as JSON array"
    )
    portfolio_values = JSONField(
        default=list,
        help_text="Daily portfolio values as JSON array"
    )
    positions_history = JSONField(
        default=list,
        help_text="Position changes history as JSON array"
    )
    trade_history = JSONField(
        default=list,
        help_text="Individual trade records as JSON array"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Results: {self.backtest.name}"
    
    @property
    def profit_factor(self) -> Optional[Decimal]:
        """Calculate profit factor (gross profits / gross losses)."""
        if self.average_loss and self.losing_trades > 0:
            gross_profits = self.average_win * self.winning_trades if self.average_win else Decimal('0')
            gross_losses = abs(self.average_loss) * self.losing_trades
            if gross_losses > 0:
                return gross_profits / gross_losses
        return None
    
    @property
    def expectancy(self) -> Optional[Decimal]:
        """Calculate trade expectancy."""
        if self.win_rate is not None and self.average_win and self.average_loss:
            return (self.win_rate * self.average_win) + ((1 - self.win_rate) * self.average_loss)
        return None


class BacktestPortfolioSnapshot(models.Model):
    """Daily portfolio snapshots during backtest execution.
    
    Tracks portfolio composition, values, and performance on each trading day
    during the backtest simulation for detailed analysis.
    """
    
    backtest = models.ForeignKey(
        Backtest,
        on_delete=models.CASCADE,
        related_name='portfolio_snapshots',
        help_text="Associated backtest run"
    )
    date = models.DateField(
        help_text="Snapshot date"
    )
    
    # Portfolio Values
    total_value = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        help_text="Total portfolio value"
    )
    cash_balance = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        help_text="Cash balance"
    )
    invested_value = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        help_text="Value invested in assets"
    )
    
    # Performance Metrics
    daily_return = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        help_text="Daily return percentage"
    )
    cumulative_return = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        help_text="Cumulative return from start"
    )
    
    # Positions
    positions = JSONField(
        default=dict,
        help_text="Current positions as JSON {symbol: {quantity, value, weight}}"
    )
    
    # Benchmark Comparison
    benchmark_value = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        help_text="Benchmark portfolio value"
    )
    benchmark_return = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        help_text="Benchmark cumulative return"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['backtest', 'date']
        constraints = [
            models.UniqueConstraint(
                fields=['backtest', 'date'],
                name='unique_backtest_snapshot_date'
            )
        ]
    
    def __str__(self):
        return f"{self.backtest.name} - {self.date}"
    
    @property
    def cash_percentage(self) -> Decimal:
        """Calculate cash as percentage of total portfolio."""
        if self.total_value > 0:
            return (self.cash_balance / self.total_value) * 100
        return Decimal('0')
    
    @property
    def invested_percentage(self) -> Decimal:
        """Calculate invested amount as percentage of total portfolio."""
        if self.total_value > 0:
            return (self.invested_value / self.total_value) * 100
        return Decimal('0')


class BacktestTrade(models.Model):
    """Individual trade execution records during backtesting.
    
    Records each buy/sell transaction executed by the strategy during
    the backtest simulation for detailed trade analysis.
    """
    
    TRADE_TYPES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
        ('short', 'Short'),
        ('cover', 'Cover'),
    ]
    
    backtest = models.ForeignKey(
        Backtest,
        on_delete=models.CASCADE,
        related_name='trades',
        help_text="Associated backtest run"
    )
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='backtest_trades',
        help_text="Asset being traded"
    )
    
    # Trade Details
    trade_type = models.CharField(
        max_length=10,
        choices=TRADE_TYPES,
        help_text="Type of trade"
    )
    date = models.DateField(
        help_text="Trade execution date"
    )
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=8,
        help_text="Number of shares/units traded"
    )
    price = models.DecimalField(
        max_digits=15,
        decimal_places=6,
        help_text="Execution price per share"
    )
    
    # Costs and Fees
    transaction_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Transaction cost/commission"
    )
    slippage_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Market impact slippage cost"
    )
    
    # Trade Value
    gross_value = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        help_text="Gross trade value (quantity * price)"
    )
    net_value = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        help_text="Net trade value after costs"
    )
    
    # Strategy Context
    signal_strength = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Strategy signal strength (0-1)"
    )
    reason = models.CharField(
        max_length=200,
        blank=True,
        help_text="Reason for trade (e.g., 'SMA crossover', 'stop loss')"
    )
    
    # Portfolio Impact
    portfolio_value_before = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        help_text="Portfolio value before trade"
    )
    portfolio_value_after = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        help_text="Portfolio value after trade"
    )
    position_size_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        help_text="Position size as percentage of portfolio"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['backtest', 'date', 'created_at']
        indexes = [
            models.Index(fields=['backtest', 'date']),
            models.Index(fields=['asset', 'trade_type']),
        ]
    
    def __str__(self):
        return f"{self.trade_type.title()} {self.quantity} {self.asset.symbol} @ ${self.price}"
    
    @property
    def total_cost(self) -> Decimal:
        """Calculate total trade cost (transaction + slippage)."""
        return self.transaction_cost + self.slippage_cost
    
    @property
    def is_opening_trade(self) -> bool:
        """Check if this is an opening trade (buy/short)."""
        return self.trade_type in ['buy', 'short']
    
    @property
    def is_closing_trade(self) -> bool:
        """Check if this is a closing trade (sell/cover)."""
        return self.trade_type in ['sell', 'cover']