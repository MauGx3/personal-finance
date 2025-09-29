Backtesting Engine Reference
============================

The backtesting engine provides a comprehensive framework for testing trading strategies against historical data with realistic market conditions.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

The backtesting engine delivers:

* **Strategy Testing**: Comprehensive framework for testing trading strategies against historical data
* **Realistic Conditions**: Transaction costs, slippage, and portfolio management constraints
* **Performance Analytics**: Detailed metrics including Sharpe ratio, max drawdown, and alpha/beta
* **Custom Strategies**: Extensible architecture for implementing custom trading algorithms
* **API Integration**: RESTful endpoints for programmatic strategy execution

.. automodule:: personal_finance.backtesting.services
   :members:
   :undoc-members:

Models Reference
----------------

Core Models
~~~~~~~~~~~

.. autoclass:: personal_finance.backtesting.models.Strategy
   :members:
   :undoc-members:

.. autoclass:: personal_finance.backtesting.models.Backtest
   :members:
   :undoc-members:

.. autoclass:: personal_finance.backtesting.models.BacktestResult
   :members:
   :undoc-members:

Strategy Types
--------------

Built-in Strategy Types
~~~~~~~~~~~~~~~~~~~~~~~

.. data:: STRATEGY_TYPES

   Available strategy types:

   * ``buy_hold`` - Buy and hold strategy
   * ``moving_average`` - Moving average crossover strategy
   * ``rsi`` - RSI mean reversion strategy
   * ``custom`` - Custom user-defined strategy

Buy & Hold Strategy
~~~~~~~~~~~~~~~~~~~

Simple buy and hold implementation:

.. code-block:: python

   from personal_finance.backtesting.services import create_strategy
   from personal_finance.backtesting.models import Backtest
   from personal_finance.backtesting.services import BacktestEngine
   from personal_finance.assets.models import Asset
   from datetime import date

   # Create strategy
   strategy = create_strategy(
       user=user,
       name="S&P 500 Buy & Hold",
       strategy_type="buy_hold",
       parameters={},
       asset_symbols=["SPY"],
       initial_capital=100000.0,
       max_position_size=1.0
   )

   # Execute backtest
   benchmark = Asset.objects.get(symbol="SPY")
   backtest = Backtest.objects.create(
       strategy=strategy,
       name="2-Year Buy & Hold Test",
       start_date=date(2022, 1, 1),
       end_date=date(2024, 1, 1),
       benchmark_asset=benchmark
   )

   engine = BacktestEngine()
   result = engine.run_backtest(backtest)

Moving Average Strategy
~~~~~~~~~~~~~~~~~~~~~~~

Moving average crossover strategy:

.. code-block:: python

   # Moving average parameters
   ma_strategy = create_strategy(
       user=user,
       name="AAPL Moving Average Strategy",
       strategy_type="moving_average",
       parameters={
           "short_window": 20,  # 20-day MA
           "long_window": 50,   # 50-day MA
       },
       asset_symbols=["AAPL"],
       initial_capital=50000.0,
       max_position_size=0.5
   )

   # Include transaction costs
   backtest = Backtest.objects.create(
       strategy=ma_strategy,
       name="AAPL MA Crossover",
       start_date=date(2023, 1, 1),
       end_date=date(2024, 1, 1),
       transaction_costs=0.001,  # 0.1%
       slippage=0.0005          # 0.05%
   )

RSI Strategy
~~~~~~~~~~~~

RSI mean reversion with risk management:

.. code-block:: python

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
       max_position_size=0.25,      # Max 25% per position
       stop_loss_percentage=0.05,   # 5% stop loss
       take_profit_percentage=0.15  # 15% take profit
   )

Custom Strategy Implementation
------------------------------

BaseStrategy Interface
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: personal_finance.backtesting.services.BaseStrategy
   :members:
   :undoc-members:

Custom Strategy Example
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from personal_finance.backtesting.services import BaseStrategy
   from personal_finance.backtesting.models import Trade
   from decimal import Decimal

   class MeanReversionStrategy(BaseStrategy):
       \"\"\"Custom mean reversion strategy based on price deviations.\"\"\"

       def generate_signals(self, current_date, portfolio):
           \"\"\"Generate trading signals based on price deviations.\"\"\"
           trades = []

           lookback_period = self.get_parameter('lookback_period', 20)
           deviation_threshold = self.get_parameter('deviation_threshold', 2.0)

           for asset in self.strategy.asset_universe.all():
               if asset.symbol not in self.price_data.columns:
                   continue

               # Calculate mean and standard deviation
               asset_prices = self.price_data[asset.symbol].dropna()
               recent_prices = asset_prices.tail(lookback_period)

               if len(recent_prices) < lookback_period:
                   continue

               mean_price = recent_prices.mean()
               std_price = recent_prices.std()
               current_price = asset_prices.loc[current_date]
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

REST API Reference
------------------

Strategy Management
~~~~~~~~~~~~~~~~~~~

.. http:get:: /api/backtesting/strategies/

   List user's trading strategies.

   **Response:**

   .. code-block:: json

      {
          "results": [
              {
                  "id": 1,
                  "name": "Tech Stock Momentum",
                  "strategy_type": "moving_average",
                  "parameters": {
                      "short_window": 15,
                      "long_window": 45
                  },
                  "initial_capital": "75000.00",
                  "max_position_size": "0.3000",
                  "asset_symbols": ["AAPL", "MSFT", "GOOGL", "NVDA"],
                  "created_at": "2024-01-15T10:30:00Z"
              }
          ]
      }

.. http:post:: /api/backtesting/strategies/

   Create a new trading strategy.

   **Request:**

   .. code-block:: json

      {
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

Backtest Execution
~~~~~~~~~~~~~~~~~~

.. http:get:: /api/backtesting/backtests/

   List user's backtests.

.. http:post:: /api/backtesting/backtests/

   Create a new backtest.

   **Request:**

   .. code-block:: json

      {
          "strategy": 1,
          "name": "Q1 2024 Tech Momentum Test",
          "start_date": "2024-01-01",
          "end_date": "2024-03-31",
          "benchmark_symbol": "QQQ",
          "transaction_costs": "0.0005",
          "slippage": "0.0003"
      }

.. http:post:: /api/backtesting/backtests/{id}/run/

   Execute a backtest.

   **Response:**

   .. code-block:: json

      {
          "status": "completed",
          "result": {
              "total_return": 12.35,
              "annualized_return": 15.42,
              "sharpe_ratio": 1.23,
              "max_drawdown": -8.45,
              "total_trades": 47,
              "win_rate": 0.68
          }
      }

Quick Backtest
~~~~~~~~~~~~~~

.. http:post:: /api/backtesting/quick-backtest/

   Create and run a backtest in one operation.

   **Request:**

   .. code-block:: json

      {
          "strategy_type": "buy_hold",
          "asset_symbols": ["SPY", "QQQ", "IWM"],
          "start_date": "2023-01-01",
          "end_date": "2024-01-01",
          "benchmark_symbol": "SPY",
          "initial_capital": 100000,
          "max_position_size": 0.4
      }

Management Commands
-------------------

.. program:: manage.py run_backtest

.. code-block:: bash

   # Create and run buy & hold strategy
   python manage.py run_backtest \\
       --create-strategy buy_hold \\
       --user admin \\
       --assets SPY QQQ IWM \\
       --period 3y \\
       --initial-capital 100000 \\
       --benchmark SPY

.. option:: --create-strategy <type>

   Create strategy of specified type (buy_hold, moving_average, rsi)

.. option:: --user <username>

   Run backtest for specified user

.. option:: --assets <symbols>

   Space-separated list of asset symbols

.. option:: --period <period>

   Time period (1y, 2y, 3y, or specific dates)

.. option:: --initial-capital <amount>

   Initial capital amount

.. option:: --benchmark <symbol>

   Benchmark asset symbol

.. option:: --dry-run

   Preview without executing

Performance Analysis
--------------------

Metrics Reference
~~~~~~~~~~~~~~~~~

.. autoclass:: personal_finance.backtesting.models.BacktestResult
   :members: total_return, annualized_return, volatility, sharpe_ratio, max_drawdown, alpha, beta

Analysis Functions
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def analyze_backtest(backtest_id):
       \"\"\"Comprehensive backtest analysis.\"\"\"
       from personal_finance.backtesting.models import Backtest

       backtest = Backtest.objects.get(id=backtest_id)
       result = backtest.result

       print(f\"\\n=== Backtest Analysis: {backtest.name} ===\")
       print(f\"Strategy: {backtest.strategy.name}\")
       print(f\"Period: {backtest.start_date} to {backtest.end_date}\")
       print(f\"Duration: {backtest.duration_days} days\")

       print(f\"\\n--- Performance Metrics ---\")
       print(f\"Total Return: {result.total_return:.2f}%\")
       print(f\"Annualized Return: {result.annualized_return:.2f}%\")
       print(f\"Volatility: {result.volatility:.2f}%\")
       print(f\"Sharpe Ratio: {result.sharpe_ratio:.2f}\")
       print(f\"Max Drawdown: {result.max_drawdown:.2f}%\")

       if result.benchmark_return:
           print(f\"\\n--- Benchmark Comparison ---\")
           print(f\"Benchmark Return: {result.benchmark_return:.2f}%\")
           print(f\"Alpha: {result.alpha:.2f}%\")
           print(f\"Beta: {result.beta:.2f}\")

Parameter Optimization
----------------------

Batch Testing
~~~~~~~~~~~~~

.. code-block:: python

   def run_parameter_sweep():
       \"\"\"Run multiple backtests with different parameters.\"\"\"
       from itertools import product

       # Parameter ranges
       short_windows = [10, 15, 20]
       long_windows = [30, 45, 60]
       assets_groups = [[\"SPY\"], [\"QQQ\"], [\"SPY\", \"QQQ\"]]

       results = []

       for short_window, long_window, assets in product(short_windows, long_windows, assets_groups):
           if short_window >= long_window:
               continue

           # Create and run backtest
           strategy = create_strategy(
               user=user,
               name=f\"MA_{short_window}_{long_window}_{'_'.join(assets)}\",
               strategy_type=\"moving_average\",
               parameters={
                   \"short_window\": short_window,
                   \"long_window\": long_window
               },
               asset_symbols=assets,
               initial_capital=100000.0
           )

           backtest = Backtest.objects.create(
               strategy=strategy,
               name=f\"Parameter Sweep {short_window}/{long_window}\",
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
                   'sharpe_ratio': float(result.sharpe_ratio),
                   'max_drawdown': float(result.max_drawdown)
               })
           except Exception as e:
               print(f\"Failed: {short_window}/{long_window} - {str(e)}\")

       # Find best performing strategy
       best_result = max(results, key=lambda x: x['sharpe_ratio'] or -999)
       print(f\"Best Strategy: MA {best_result['short_window']}/{best_result['long_window']}\")
       print(f\"Assets: {best_result['assets']}\")
       print(f\"Sharpe Ratio: {best_result['sharpe_ratio']:.2f}\")

Error Handling
--------------

Data Validation
~~~~~~~~~~~~~~~

.. code-block:: python

   def validate_backtest_data(backtest):
       \"\"\"Validate that backtest has sufficient data.\"\"\"
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
           print(f\"Warning: Insufficient data for: {missing_data}\")

       return len(missing_data) == 0

Debug Failed Backtests
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def debug_backtest_failure(backtest_id):
       \"\"\"Debug a failed backtest.\"\"\"
       backtest = Backtest.objects.get(id=backtest_id)

       print(f\"Backtest: {backtest.name}\")
       print(f\"Status: {backtest.status}\")
       print(f\"Error: {backtest.error_message}\")

       # Check strategy configuration
       strategy = backtest.strategy
       print(f\"\\nStrategy: {strategy.name}\")
       print(f\"Type: {strategy.strategy_type}\")
       print(f\"Assets: {list(strategy.asset_universe.values_list('symbol', flat=True))}\")
       print(f\"Parameters: {strategy.parameters}\")

       # Validate data availability
       validate_backtest_data(backtest)

Performance Optimization
------------------------

Database Optimization
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Use select_related and prefetch_related
   backtests = Backtest.objects.select_related(
       'strategy', 'benchmark_asset'
   ).prefetch_related(
       'strategy__asset_universe'
   )

   # Batch create operations
   from django.db import transaction

   @transaction.atomic
   def batch_create_snapshots(snapshots_data):
       \"\"\"Batch create portfolio snapshots.\"\"\"
       snapshots = [
           BacktestPortfolioSnapshot(**data)
           for data in snapshots_data
       ]
       BacktestPortfolioSnapshot.objects.bulk_create(snapshots)

Memory Management
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Process large datasets with iterator
   for backtest in Backtest.objects.filter(status='pending').iterator():
       process_backtest(backtest)

   # Limit date ranges for testing
   short_backtest = Backtest.objects.create(
       strategy=strategy,
       name=\"Quick Test\",
       start_date=date(2024, 1, 1),
       end_date=date(2024, 2, 1)  # One month for quick testing
   )

See Also
--------

* :doc:`../api/rest_endpoints` - Complete API reference
* :doc:`analytics` - Portfolio analytics integration
* :doc:`../development/testing` - Testing strategies and backtests
