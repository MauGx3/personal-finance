# Backtesting Engine - Usage Guide

This document provides comprehensive usage examples for the backtesting engine, designed to help both junior and senior developers implement and test trading strategies.

## Overview

The backtesting engine provides a comprehensive framework for testing trading strategies against historical data with realistic market conditions including transaction costs, slippage, and portfolio management constraints.

## Quick Start

### 1. Create a Simple Buy & Hold Strategy

```python
from personal_finance.backtesting.services import create_strategy
from personal_finance.backtesting.models import Backtest
from personal_finance.backtesting.services import BacktestEngine
from personal_finance.assets.models import Asset
from datetime import date

# Create a simple buy and hold strategy
strategy = create_strategy(
    user=user,  # Django user instance
    name="S&P 500 Buy & Hold",
    strategy_type="buy_hold",
    parameters={},
    asset_symbols=["SPY"],
    initial_capital=100000.0,
    max_position_size=1.0  # 100% allocation allowed
)

# Create and run backtest
benchmark = Asset.objects.get(symbol="SPY")
backtest = Backtest.objects.create(
    strategy=strategy,
    name="2-Year Buy & Hold Test",
    start_date=date(2022, 1, 1),
    end_date=date(2024, 1, 1),
    benchmark_asset=benchmark
)

# Execute backtest
engine = BacktestEngine()
result = engine.run_backtest(backtest)

print(f"Total Return: {result.total_return:.2f}%")
print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
print(f"Max Drawdown: {result.max_drawdown:.2f}%")
```

### 2. Moving Average Crossover Strategy

```python
# Create moving average strategy
ma_strategy = create_strategy(
    user=user,
    name="AAPL Moving Average Strategy",
    strategy_type="moving_average",
    parameters={
        "short_window": 20,  # 20-day moving average
        "long_window": 50,   # 50-day moving average
    },
    asset_symbols=["AAPL"],
    initial_capital=50000.0,
    max_position_size=0.5  # Maximum 50% in any position
)

# Create backtest with transaction costs
backtest = Backtest.objects.create(
    strategy=ma_strategy,
    name="AAPL MA Crossover",
    start_date=date(2023, 1, 1),
    end_date=date(2024, 1, 1),
    transaction_costs=0.001,  # 0.1% transaction cost
    slippage=0.0005          # 0.05% slippage
)

result = engine.run_backtest(backtest)
```

### 3. RSI Mean Reversion Strategy

```python
# Create RSI strategy
rsi_strategy = create_strategy(
    user=user,
    name="Multi-Asset RSI Strategy",
    strategy_type="rsi",
    parameters={
        "rsi_period": 14,
        "oversold_threshold": 30,
        "overbought_threshold": 70
    },
    asset_symbols=["AAPL", "MSFT", "GOOGL", "AMZN"],
    initial_capital=100000.0,
    max_position_size=0.25,  # Max 25% per position
    stop_loss_percentage=0.05,  # 5% stop loss
    take_profit_percentage=0.15  # 15% take profit
)
```

## Management Commands

### Running Backtests from Command Line

```bash
# Create and run a buy & hold strategy
python manage.py run_backtest \
    --create-strategy buy_hold \
    --user admin \
    --assets SPY QQQ IWM \
    --period 3y \
    --initial-capital 100000 \
    --benchmark SPY

# Moving average strategy with custom parameters
python manage.py run_backtest \
    --create-strategy moving_average \
    --user admin \
    --assets AAPL MSFT \
    --short-window 10 \
    --long-window 30 \
    --start-date 2022-01-01 \
    --end-date 2023-12-31

# RSI strategy
python manage.py run_backtest \
    --create-strategy rsi \
    --user admin \
    --assets SPY \
    --rsi-period 14 \
    --oversold-threshold 25 \
    --overbought-threshold 75 \
    --max-position-size 0.5

# Run specific backtest
python manage.py run_backtest --backtest-id 123

# Run all pending backtests
python manage.py run_backtest --all-pending

# Dry run to see what would happen
python manage.py run_backtest \
    --create-strategy buy_hold \
    --user admin \
    --assets AAPL \
    --dry-run
```

## API Usage

### Creating Strategies via API

```python
import requests

# Create strategy
strategy_data = {
    "name": "Tech Stock Momentum",
    "strategy_type": "moving_average",
    "description": "Momentum strategy for tech stocks",
    "parameters": {
        "short_window": 15,
        "long_window": 45
    },
    "initial_capital": "75000.00",
    "max_position_size": "0.3000",
    "asset_symbols": ["AAPL", "MSFT", "GOOGL", "NVDA"]
}

response = requests.post(
    "http://localhost:8000/api/backtesting/strategies/",
    json=strategy_data,
    headers={"Authorization": "Token your-token-here"}
)
strategy = response.json()
```

### Running Backtests via API

```python
# Create backtest
backtest_data = {
    "strategy": strategy["id"],
    "name": "Q1 2024 Tech Momentum Test",
    "start_date": "2024-01-01",
    "end_date": "2024-03-31",
    "benchmark_symbol": "QQQ",
    "transaction_costs": "0.0005",
    "slippage": "0.0003"
}

response = requests.post(
    "http://localhost:8000/api/backtesting/backtests/",
    json=backtest_data,
    headers={"Authorization": "Token your-token-here"}
)
backtest = response.json()

# Run the backtest
response = requests.post(
    f"http://localhost:8000/api/backtesting/backtests/{backtest['id']}/run/",
    headers={"Authorization": "Token your-token-here"}
)
result = response.json()
```

### Quick Backtest

```python
# Create and run backtest in one call
quick_data = {
    "strategy_type": "buy_hold",
    "asset_symbols": ["SPY", "QQQ", "IWM"],
    "start_date": "2023-01-01",
    "end_date": "2024-01-01",
    "benchmark_symbol": "SPY",
    "initial_capital": 100000,
    "max_position_size": 0.4
}

response = requests.post(
    "http://localhost:8000/api/backtesting/quick-backtest/",
    json=quick_data,
    headers={"Authorization": "Token your-token-here"}
)
```

## Advanced Usage

### Custom Strategy Implementation

```python
from personal_finance.backtesting.services import BaseStrategy
from personal_finance.backtesting.models import Trade
from decimal import Decimal

class MeanReversionStrategy(BaseStrategy):
    """Custom mean reversion strategy based on price deviations."""
    
    def generate_signals(self, current_date, portfolio):
        """Generate trading signals based on price deviations."""
        trades = []
        
        lookback_period = self.get_parameter('lookback_period', 20)
        deviation_threshold = self.get_parameter('deviation_threshold', 2.0)
        
        for asset in self.strategy.asset_universe.all():
            if asset.symbol not in self.price_data.columns:
                continue
                
            # Get recent prices
            asset_prices = self.price_data[asset.symbol].dropna()
            recent_prices = asset_prices.tail(lookback_period)
            
            if len(recent_prices) < lookback_period:
                continue
                
            # Calculate mean and standard deviation
            mean_price = recent_prices.mean()
            std_price = recent_prices.std()
            current_price = asset_prices.loc[current_date]
            
            # Calculate deviation from mean
            deviation = (current_price - mean_price) / std_price
            
            current_position = portfolio.get_position(asset.symbol)
            max_position_value = portfolio.total_value * self.strategy.max_position_size
            
            # Buy signal: price significantly below mean
            if (deviation < -deviation_threshold and 
                current_position.quantity == 0):
                
                quantity = max_position_value / Decimal(str(current_price))
                trades.append(Trade(
                    asset=asset,
                    quantity=quantity,
                    trade_type='buy',
                    signal_strength=abs(Decimal(str(deviation))),
                    reason=f'Mean reversion buy: {deviation:.2f} std below mean'
                ))
            
            # Sell signal: price significantly above mean
            elif (deviation > deviation_threshold and 
                  current_position.quantity > 0):
                
                trades.append(Trade(
                    asset=asset,
                    quantity=current_position.quantity,
                    trade_type='sell',
                    signal_strength=Decimal(str(deviation)),
                    reason=f'Mean reversion sell: {deviation:.2f} std above mean'
                ))
        
        return trades

# Register custom strategy
from personal_finance.backtesting.services import STRATEGY_REGISTRY
STRATEGY_REGISTRY['mean_reversion'] = MeanReversionStrategy
```

### Portfolio Analysis

```python
# Analyze backtest results
def analyze_backtest(backtest_id):
    """Comprehensive backtest analysis."""
    from personal_finance.backtesting.models import Backtest
    
    backtest = Backtest.objects.get(id=backtest_id)
    result = backtest.result
    
    print(f"\n=== Backtest Analysis: {backtest.name} ===")
    print(f"Strategy: {backtest.strategy.name}")
    print(f"Period: {backtest.start_date} to {backtest.end_date}")
    print(f"Duration: {backtest.duration_days} days")
    
    print(f"\n--- Performance Metrics ---")
    print(f"Total Return: {result.total_return:.2f}%")
    print(f"Annualized Return: {result.annualized_return:.2f}%")
    print(f"Volatility: {result.volatility:.2f}%")
    print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}" if result.sharpe_ratio else "Sharpe Ratio: N/A")
    print(f"Max Drawdown: {result.max_drawdown:.2f}%")
    
    print(f"\n--- Trading Statistics ---")
    print(f"Total Trades: {result.total_trades}")
    print(f"Win Rate: {result.win_rate*100:.1f}%" if result.win_rate else "Win Rate: N/A")
    print(f"Average Win: {result.average_win:.2f}%" if result.average_win else "Average Win: N/A")
    print(f"Average Loss: {result.average_loss:.2f}%" if result.average_loss else "Average Loss: N/A")
    print(f"Profit Factor: {result.profit_factor:.2f}" if result.profit_factor else "Profit Factor: N/A")
    
    if result.benchmark_return:
        print(f"\n--- Benchmark Comparison ---")
        print(f"Benchmark Return: {result.benchmark_return:.2f}%")
        print(f"Alpha: {result.alpha:.2f}%" if result.alpha else "Alpha: N/A")
        print(f"Beta: {result.beta:.2f}" if result.beta else "Beta: N/A")
        print(f"Information Ratio: {result.information_ratio:.2f}" if result.information_ratio else "Info Ratio: N/A")
    
    print(f"\n--- Portfolio Statistics ---")
    print(f"Final Value: ${result.final_portfolio_value:,.2f}")
    print(f"Total Transaction Costs: ${result.total_transaction_costs:,.2f}")
```

### Batch Backtesting

```python
def run_parameter_sweep():
    """Run multiple backtests with different parameters."""
    from itertools import product
    
    # Parameter ranges
    short_windows = [10, 15, 20]
    long_windows = [30, 45, 60]
    assets_groups = [["SPY"], ["QQQ"], ["SPY", "QQQ"]]
    
    results = []
    
    for short_window, long_window, assets in product(short_windows, long_windows, assets_groups):
        if short_window >= long_window:
            continue
            
        # Create strategy
        strategy = create_strategy(
            user=user,
            name=f"MA_{short_window}_{long_window}_{'_'.join(assets)}",
            strategy_type="moving_average",
            parameters={
                "short_window": short_window,
                "long_window": long_window
            },
            asset_symbols=assets,
            initial_capital=100000.0
        )
        
        # Create and run backtest
        backtest = Backtest.objects.create(
            strategy=strategy,
            name=f"Parameter Sweep {short_window}/{long_window}",
            start_date=date(2022, 1, 1),
            end_date=date(2024, 1, 1)
        )
        
        try:
            result = engine.run_backtest(backtest)
            results.append({
                'short_window': short_window,
                'long_window': long_window,
                'assets': assets,
                'total_return': float(result.total_return),
                'sharpe_ratio': float(result.sharpe_ratio) if result.sharpe_ratio else None,
                'max_drawdown': float(result.max_drawdown)
            })
        except Exception as e:
            print(f"Failed: {short_window}/{long_window} - {str(e)}")
    
    # Analyze results
    best_result = max(results, key=lambda x: x['sharpe_ratio'] if x['sharpe_ratio'] else -999)
    print(f"Best Strategy: MA {best_result['short_window']}/{best_result['long_window']}")
    print(f"Assets: {best_result['assets']}")
    print(f"Sharpe Ratio: {best_result['sharpe_ratio']:.2f}")
```

## Error Handling and Debugging

### Common Issues and Solutions

```python
# Check for missing price data
def validate_backtest_data(backtest):
    """Validate that backtest has sufficient data."""
    from personal_finance.assets.models import PriceHistory
    
    missing_data = []
    for asset in backtest.strategy.asset_universe.all():
        price_count = PriceHistory.objects.filter(
            asset=asset,
            date__gte=backtest.start_date,
            date__lte=backtest.end_date
        ).count()
        
        expected_days = (backtest.end_date - backtest.start_date).days
        if price_count < expected_days * 0.8:  # Allow for weekends/holidays
            missing_data.append(asset.symbol)
    
    if missing_data:
        print(f"Warning: Insufficient data for: {missing_data}")
    
    return len(missing_data) == 0

# Debug failed backtest
def debug_backtest_failure(backtest_id):
    """Debug a failed backtest."""
    backtest = Backtest.objects.get(id=backtest_id)
    
    print(f"Backtest: {backtest.name}")
    print(f"Status: {backtest.status}")
    print(f"Error: {backtest.error_message}")
    
    # Check strategy configuration
    strategy = backtest.strategy
    print(f"\nStrategy: {strategy.name}")
    print(f"Type: {strategy.strategy_type}")
    print(f"Assets: {list(strategy.asset_universe.values_list('symbol', flat=True))}")
    print(f"Parameters: {strategy.parameters}")
    
    # Validate data availability
    validate_backtest_data(backtest)
```

## Performance Optimization

### Tips for Large Backtests

```python
# Optimize for large datasets
def optimize_backtest_performance():
    """Tips for optimizing backtest performance."""
    
    # 1. Use select_related and prefetch_related
    backtests = Backtest.objects.select_related(
        'strategy', 'benchmark_asset'
    ).prefetch_related(
        'strategy__asset_universe'
    )
    
    # 2. Batch create snapshots and trades
    from django.db import transaction
    
    @transaction.atomic
    def batch_create_snapshots(snapshots_data):
        """Batch create portfolio snapshots."""
        snapshots = [
            BacktestPortfolioSnapshot(**data) 
            for data in snapshots_data
        ]
        BacktestPortfolioSnapshot.objects.bulk_create(snapshots)
    
    # 3. Use iterator for large querysets
    for backtest in Backtest.objects.filter(status='pending').iterator():
        process_backtest(backtest)
    
    # 4. Limit backtest date ranges for initial testing
    short_backtest = Backtest.objects.create(
        strategy=strategy,
        name="Quick Test",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 2, 1)  # One month for quick testing
    )
```

This comprehensive guide provides everything needed to effectively use the backtesting engine, from simple examples to advanced custom strategy implementation and performance optimization techniques.