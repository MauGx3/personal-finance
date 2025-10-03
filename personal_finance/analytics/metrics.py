"""Lightweight financial metrics utilities.

This module collects deterministic, dependency-free helpers for common
portfolio analytics. The intent is to make core formulas reusable across the
codebase (services, CLI tooling, docs) while keeping the implementations easy
to reason about and well tested.

All functions avoid network calls and external data providers so they can be
exercised in unit tests without additional fixtures.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from math import sqrt
from statistics import mean
from typing import Sequence


DecimalLike = float | int | Decimal


def _to_float(value: DecimalLike) -> float:
    """Convert value to ``float``, handling ``Decimal`` inputs."""

    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def _to_decimal(value: DecimalLike) -> Decimal:
    """Convert numeric input to :class:`~decimal.Decimal`.

    ``Decimal(str(value))`` is preferred over ``Decimal(value)`` for floats to
    avoid binary floating point artefacts.
    """

    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        # pragma: no cover - defensive
        raise ValueError(f"Cannot convert value '{value}' to Decimal") from exc


def compound_annual_growth_rate(
    beginning_value: DecimalLike,
    ending_value: DecimalLike,
    years: float,
) -> float | None:
    """Return the compound annual growth rate.

    The result is expressed as a decimal fraction (e.g. 0.0845 == 8.45%).
    """

    start = _to_float(beginning_value)
    end = _to_float(ending_value)
    if start <= 0 or years <= 0:
        return None
    return (end / start) ** (1 / years) - 1


def sharpe_ratio(
    returns: Sequence[float],
    risk_free_rate: float = 0.0,
) -> float | None:
    """Calculate the Sharpe ratio for *returns*.

    ``returns`` should contain periodic (e.g. daily) return values expressed as
    decimal fractions (0.01 == 1%). The function returns ``None`` when the
    inputs are insufficient to compute a standard deviation.
    """

    if len(returns) < 2:
        return None
    avg_return = mean(returns)
    variance = sum((r - avg_return) ** 2 for r in returns) / (len(returns) - 1)
    std_dev = sqrt(variance)
    if std_dev == 0:
        return None
    return (avg_return - risk_free_rate) / std_dev


def value_at_risk(
    returns: Sequence[float],
    confidence_level: float = 0.95,
) -> float | None:
    """Historical Value at Risk (VaR).

    Returns the maximum expected loss (positive number) at the supplied
    confidence level. ``None`` is returned for empty datasets.
    """

    if not returns:
        return None
    sorted_returns = sorted(returns)
    index = int((1 - confidence_level) * len(sorted_returns))
    index = max(0, min(index, len(sorted_returns) - 1))
    return -sorted_returns[index]


def beta(
    asset_returns: Sequence[float],
    market_returns: Sequence[float],
) -> float | None:
    """Compute the beta coefficient for an asset versus a benchmark."""

    if len(asset_returns) != len(market_returns) or len(asset_returns) < 2:
        return None
    asset_avg = mean(asset_returns)
    market_avg = mean(market_returns)
    covariance = sum(
        (a - asset_avg) * (m - market_avg)
        for a, m in zip(asset_returns, market_returns)
    ) / (len(asset_returns) - 1)
    market_variance = sum((m - market_avg) ** 2 for m in market_returns) / (
        len(market_returns) - 1
    )
    if market_variance == 0:
        return None
    return covariance / market_variance


def weighted_return(
    weights: Sequence[float],
    returns: Sequence[float],
) -> float | None:
    """Weighted portfolio return.

    Weights must sum to one (within a 0.1% tolerance). ``None`` is returned for
    mismatched lengths or invalid sums.
    """

    if len(weights) != len(returns):
        return None
    if abs(sum(weights) - 1.0) > 0.001:
        return None
    return sum(w * r for w, r in zip(weights, returns))


def rebalancing_trades(
    current_values: Sequence[float],
    target_weights: Sequence[float],
    total_value: float,
) -> dict[str, float] | None:
    """Return the trade amounts required to reach *target_weights*.

    Positive numbers indicate buys; negative numbers indicate sells.
    """

    if len(current_values) != len(target_weights):
        return None
    if abs(sum(target_weights) - 1.0) > 0.001:
        return None
    trades: dict[str, float] = {}
    for idx, (current, target_weight) in enumerate(
        zip(current_values, target_weights)
    ):
        target_value = total_value * target_weight
        trades[f"asset_{idx}"] = target_value - current
    return trades


def maximum_drawdown(values: Sequence[float]) -> float | None:
    """Return the maximum drawdown (fraction of peak value)."""

    if len(values) < 2:
        return None
    peak = values[0]
    max_dd = 0.0
    for value in values[1:]:
        if value > peak:
            peak = value
        else:
            drawdown = (peak - value) / peak if peak != 0 else 0
            max_dd = max(max_dd, drawdown)
    return max_dd


def downside_deviation(
    returns: Sequence[float],
    target_return: float = 0.0,
) -> float:
    """Downside deviation (a measure of downside risk)."""

    downside = [r for r in returns if r < target_return]
    if not downside:
        return 0.0
    variance = sum((r - target_return) ** 2 for r in downside) / len(downside)
    return sqrt(variance)


def business_days_between(start_date: date, end_date: date) -> int:
    """Count business days (Mon–Fri) inclusive between two dates."""

    if start_date > end_date:
        return 0
    current = start_date
    business_days = 0
    while current <= end_date:
        if current.weekday() < 5:
            business_days += 1
        current += timedelta(days=1)
    return business_days


def annualized_return(total_return: float, days: int) -> float | None:
    """Convert a cumulative return over *days* to an annualised figure."""

    if days <= 0:
        return None
    years = days / 365.25
    if years == 0:
        return None
    return (1 + total_return) ** (1 / years) - 1


def round_currency(value: DecimalLike) -> Decimal:
    """Round monetary amounts to two decimal places using ``ROUND_HALF_UP``."""

    return _to_decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def percentage_change(
    old_value: DecimalLike,
    new_value: DecimalLike,
) -> Decimal | None:
    """Percentage change between two values with two-decimal precision."""

    old_dec = _to_decimal(old_value)
    new_dec = _to_decimal(new_value)
    if old_dec == 0:
        return None
    change = ((new_dec - old_dec) / old_dec) * Decimal("100")
    return change.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def validate_positive(
    value: DecimalLike | None,
    field_name: str = "value",
) -> bool:
    """Ensure *value* is positive, raising :class:`ValueError` otherwise."""

    if value is None:
        raise ValueError(f"{field_name} cannot be None")
    if _to_decimal(value) <= 0:
        raise ValueError(f"{field_name} must be positive")
    return True


def validate_percentage(
    value: float | None,
    min_pct: float = 0,
    max_pct: float = 100,
) -> bool:
    """Validate that a percentage lies between ``min_pct`` and ``max_pct``."""

    if value is None:
        raise ValueError("Percentage cannot be None")
    if value < min_pct or value > max_pct:
        raise ValueError(
            f"Percentage must be between {min_pct}% and {max_pct}%"
        )
    return True


def sortino_ratio(
    returns: Sequence[float],
    target_return: float = 0.0,
) -> float | None:
    """Sortino ratio – risk-adjusted return using downside deviation."""

    if not returns:
        return None
    avg_return = mean(returns)
    downside = downside_deviation(returns, target_return)
    if downside == 0:
        return float("inf") if avg_return > target_return else None
    return (avg_return - target_return) / downside


def information_ratio(
    portfolio_returns: Sequence[float],
    benchmark_returns: Sequence[float],
) -> float | None:
    """Information ratio comparing portfolio and benchmark returns."""

    if (
        len(portfolio_returns) != len(benchmark_returns)
        or not portfolio_returns
    ):
        return None
    excess = [p - b for p, b in zip(portfolio_returns, benchmark_returns)]
    if len(excess) < 2:
        return None
    avg_excess = mean(excess)
    variance = sum((e - avg_excess) ** 2 for e in excess) / (len(excess) - 1)
    tracking_error = sqrt(variance)
    if tracking_error == 0:
        return None
    return avg_excess / tracking_error


@dataclass(frozen=True)
class RebalanceInstruction:
    """Structured representation of a rebalance recommendation."""

    symbol: str
    amount: float

    @staticmethod
    def from_mapping(
        mapping: dict[str, float],
    ) -> Sequence[RebalanceInstruction]:
        """Convert a mapping produced by :func:`rebalancing_trades`.

        This helper is useful for higher-level services that need structured
        outputs while the lower-level helper remains lightweight for testing.
        """

        return [
            RebalanceInstruction(symbol=symbol, amount=amount)
            for symbol, amount in mapping.items()
        ]
