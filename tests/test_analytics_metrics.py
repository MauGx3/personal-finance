"""Tests for :mod:`personal_finance.analytics.metrics`."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from personal_finance.analytics import metrics
from personal_finance.analytics.metrics import RebalanceInstruction


def test_compound_annual_growth_rate_basics() -> None:
    result = metrics.compound_annual_growth_rate(100_000, 150_000, 5)
    assert result is not None
    assert result == pytest.approx(0.0845, rel=1e-3)

    assert metrics.compound_annual_growth_rate(0, 150_000, 5) is None
    assert metrics.compound_annual_growth_rate(100_000, 150_000, 0) is None


def test_sharpe_ratio_and_edge_cases() -> None:
    returns = [0.10, 0.15, 0.08, 0.12, 0.20, 0.05, 0.18]
    sharpe = metrics.sharpe_ratio(returns, risk_free_rate=0.03)
    assert sharpe is not None
    assert sharpe > 0

    assert metrics.sharpe_ratio([]) is None
    assert metrics.sharpe_ratio([0.1]) is None
    assert metrics.sharpe_ratio([0.1, 0.1, 0.1]) is None


def test_value_at_risk_historical() -> None:
    returns = [0.10, -0.05, 0.08, -0.12, 0.15, -0.03, 0.20, -0.08, 0.05]
    var_95 = metrics.value_at_risk(returns, confidence_level=0.95)
    assert var_95 is not None
    assert var_95 > 0

    assert metrics.value_at_risk([]) is None


def test_beta_calculation() -> None:
    asset_returns = [0.10, 0.15, 0.05, 0.20, 0.12]
    market_returns = [0.08, 0.12, 0.04, 0.15, 0.10]

    beta = metrics.beta(asset_returns, market_returns)
    assert beta is not None
    assert beta > 0

    assert metrics.beta([], []) is None
    assert metrics.beta([0.1], [0.1]) is None
    assert metrics.beta([0.1, 0.2], [0.1]) is None


def test_weighted_return_validation() -> None:
    weights = [0.4, 0.3, 0.2, 0.1]
    returns = [0.10, 0.15, 0.08, 0.20]

    portfolio_return = metrics.weighted_return(weights, returns)
    expected = sum(w * r for w, r in zip(weights, returns))
    assert portfolio_return == pytest.approx(expected)

    assert metrics.weighted_return([0.5, 0.5], [0.1]) is None
    assert metrics.weighted_return([0.6, 0.5], [0.1, 0.2]) is None


def test_rebalancing_trades_helper() -> None:
    current_values = [40_000, 35_000, 25_000]
    target_weights = [0.5, 0.3, 0.2]
    total_value = 100_000

    trades = metrics.rebalancing_trades(
        current_values, target_weights, total_value
    )
    assert trades == {
        "asset_0": pytest.approx(10_000),
        "asset_1": pytest.approx(-5_000),
        "asset_2": pytest.approx(-5_000),
    }

    assert metrics.rebalancing_trades([1, 2], [0.5], 10_000) is None


def test_maximum_drawdown() -> None:
    values = [100_000, 110_000, 115_000, 105_000, 95_000, 102_000, 120_000]
    result = metrics.maximum_drawdown(values)
    expected = (115_000 - 95_000) / 115_000
    assert result == pytest.approx(expected)

    assert metrics.maximum_drawdown([100_000]) is None


def test_downside_deviation_behavior() -> None:
    returns = [0.10, -0.05, 0.08, -0.12, 0.15, -0.03, 0.20]
    downside = metrics.downside_deviation(returns)
    negatives = [-0.05, -0.12, -0.03]
    expected = (sum(r**2 for r in negatives) / len(negatives)) ** 0.5
    assert downside == pytest.approx(expected)

    assert metrics.downside_deviation([0.1, 0.2]) == 0


def test_business_days_between_inclusive() -> None:
    monday = date(2024, 1, 15)
    friday = date(2024, 1, 19)
    assert metrics.business_days_between(monday, friday) == 5

    sunday = date(2024, 1, 21)
    assert metrics.business_days_between(monday, sunday) == 5

    assert metrics.business_days_between(friday, monday) == 0


def test_annualized_return_and_helpers() -> None:
    result = metrics.annualized_return(0.05, 180)
    assert result is not None
    assert result > 0.05

    assert metrics.annualized_return(0.05, 0) is None

    assert metrics.round_currency(Decimal("123.456")) == Decimal("123.46")

    change = metrics.percentage_change(Decimal("100"), Decimal("105.50"))
    assert change == Decimal("5.50")
    assert metrics.percentage_change(0, 10) is None


def test_validation_helpers() -> None:
    assert metrics.validate_positive(Decimal("1")) is True
    with pytest.raises(ValueError):
        metrics.validate_positive(None)
    with pytest.raises(ValueError):
        metrics.validate_positive(Decimal("0"))

    assert metrics.validate_percentage(50.0) is True
    with pytest.raises(ValueError):
        metrics.validate_percentage(-1)
    with pytest.raises(ValueError):
        metrics.validate_percentage(101)


def test_sortino_and_information_ratios() -> None:
    returns = [0.10, -0.05, 0.15, -0.02, 0.20, 0.08, -0.10]
    sortino = metrics.sortino_ratio(returns)
    assert sortino is not None
    assert sortino > 0

    assert metrics.sortino_ratio([]) is None

    portfolio = [0.12, 0.08, 0.15, 0.10, 0.18]
    benchmark = [0.10, 0.06, 0.12, 0.08, 0.14]
    info_ratio = metrics.information_ratio(portfolio, benchmark)
    assert info_ratio is not None
    assert info_ratio > 0

    assert metrics.information_ratio([0.1], []) is None


def test_rebalance_instruction_helpers() -> None:
    mapping = {"asset_0": 1000.0, "asset_1": -500.0}
    instructions = RebalanceInstruction.from_mapping(mapping)
    assert instructions == [
        RebalanceInstruction(symbol="asset_0", amount=1000.0),
        RebalanceInstruction(symbol="asset_1", amount=-500.0),
    ]
