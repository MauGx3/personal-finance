Analytics Module
=================

The analytics module provides deterministic, dependency-light helpers for
financial metrics that are safe to execute inside unit tests and offline data
pipelines. These utilities power reporting endpoints, scheduled tasks, and
notebook workflows without requiring external services.

.. contents::
   :local:
   :depth: 2

Design Goals
------------

- **Deterministic** – all helpers operate purely on the inputs supplied by the
  caller so they can be validated with small fixtures.
- **Precise** – functions accept ``Decimal`` inputs where appropriate to avoid
  floating-point drift for currency calculations.
- **Composable** – helpers can be chained together (for example, compute
  downside deviation, then feed the result into the Sortino ratio), enabling
  higher-level services to stay focused on orchestration.

Key Helpers
-----------

The table below summarises the most frequently used helpers exposed in
``personal_finance.analytics.metrics``.

.. list-table::
   :header-rows: 1

   * - Helper
     - Purpose
     - Notes
   * - ``compound_annual_growth_rate``
     - Converts cumulative performance into an annualised growth rate.
     - Returns ``None`` if the starting value or duration is invalid.
   * - ``sharpe_ratio`` / ``sortino_ratio``
     - Risk-adjusted return metrics calculated from periodic returns.
     - ``None`` is returned when the dataset is too small or the volatility is
       zero.
   * - ``value_at_risk``
     - Historical VaR implementation that estimates the maximum loss at a
       chosen confidence level.
     - Expressed as a positive number to emphasise magnitude of loss.
   * - ``beta``
     - Measures sensitivity of an asset or strategy relative to a benchmark.
     - Requires matching sequence lengths and at least two observations.
   * - ``weighted_return``
     - Computes the portfolio return from matching weight and return vectors.
     - Validates that weights sum to 1 (±0.1%).
   * - ``rebalancing_trades``
     - Suggests buy/sell amounts needed to reach a new allocation.
     - Also exposes ``RebalanceInstruction`` for structured responses.
   * - ``maximum_drawdown`` / ``downside_deviation``
     - Downside risk helpers that feed into other analytics such as Sortino or
       stress reporting.
     - Return ``None`` or ``0.0`` when insufficient data exists.
   * - ``percentage_change`` / ``round_currency`` / ``validate_positive``
     - Small validation and formatting helpers shared across services and
       Celery tasks.

Example Usage
-------------

.. code-block:: python

   from decimal import Decimal
   from personal_finance.analytics import metrics

   monthly_returns = [0.02, 0.01, -0.03, 0.04, 0.015, 0.005]

   sharpe = metrics.sharpe_ratio(monthly_returns, risk_free_rate=0.01)
   sortino = metrics.sortino_ratio(monthly_returns)
   drawdown = metrics.maximum_drawdown([100_000, 110_000, 95_000, 120_000])

   rebalance = metrics.rebalancing_trades(
       current_values=[40_000, 35_000, 25_000],
       target_weights=[0.5, 0.3, 0.2],
       total_value=100_000,
   )

   change = metrics.percentage_change(Decimal("100"), Decimal("105.50"))

Testing Guidance
----------------

Unit tests for the analytics helpers live in
``tests/test_analytics_metrics.py``. They focus on:

- Happy paths covering real-world financial scenarios.
- Edge cases that should gracefully return ``None`` (e.g., insufficient data).
- Validation of decimal precision for currency-sensitive calculations.

When extending the module, aim to keep inputs collection-free and consider
adding additional fixtures to the existing test module so coverage remains
focused and fast.
