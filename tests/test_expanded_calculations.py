"""
Expanded test suite for financial calculations and utilities.

This test file expands coverage for financial calculations, utility functions,
and data processing that don't require complex model migrations.
"""

import pytest
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta


class TestFinancialCalculations:
    """Test fundamental financial calculation functions."""

    def test_compound_annual_growth_rate(self):
        """Test CAGR calculation."""

        def calculate_cagr(beginning_value, ending_value, years):
            """Calculate Compound Annual Growth Rate (CAGR).

            Formula: CAGR = (Ending Value / Beginning Value)^(1/n) - 1
            where n is the number of years.
            """
            if beginning_value <= 0 or years <= 0:
                return None
            return (float(ending_value) / float(beginning_value)) ** (1 / years) - 1

        # Test standard CAGR calculation
        cagr = calculate_cagr(
            beginning_value=Decimal("100000"),
            ending_value=Decimal("150000"),
            years=5,
        )
        expected = (1.5) ** (1 / 5) - 1  # About 8.45%
        assert abs(float(cagr) - expected) < 0.001

        # Test edge cases
        assert calculate_cagr(0, 150000, 5) is None
        assert calculate_cagr(100000, 150000, 0) is None
        assert calculate_cagr(-100000, 150000, 5) is None

    def test_sharpe_ratio_calculation(self):
        """Test Sharpe ratio calculation."""

        def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
            """Calculate Sharpe ratio.

            Formula: Sharpe Ratio = (Portfolio Return - Risk Free Rate) / Standard Deviation
            """
            if not returns or len(returns) < 2:
                return None

            avg_return = sum(returns) / len(returns)

            # Calculate standard deviation
            variance = sum((r - avg_return) ** 2 for r in returns) / (
                len(returns) - 1
            )
            std_dev = variance**0.5

            if std_dev == 0:
                return None

            return (avg_return - risk_free_rate) / std_dev

        # Test with sample returns
        returns = [0.10, 0.15, 0.08, 0.12, 0.20, 0.05, 0.18]
        sharpe = calculate_sharpe_ratio(returns, risk_free_rate=0.03)

        assert sharpe is not None
        assert sharpe > 0  # Should be positive for good performance

        # Test edge cases
        assert calculate_sharpe_ratio([]) is None
        assert calculate_sharpe_ratio([0.1]) is None
        assert (
            calculate_sharpe_ratio([0.1, 0.1, 0.1, 0.1]) is None
        )  # Zero std dev

    def test_value_at_risk_calculation(self):
        """Test Value at Risk (VaR) calculation."""

        def calculate_var(returns, confidence_level=0.95):
            """Calculate Value at Risk using historical method.

            VaR represents the maximum expected loss at a given confidence level.
            """
            if not returns:
                return None

            sorted_returns = sorted(returns)
            index = int((1 - confidence_level) * len(sorted_returns))

            # Handle edge case for small datasets
            if index >= len(sorted_returns):
                index = len(sorted_returns) - 1

            return -sorted_returns[index]  # Negative because it's a loss

        # Test with sample returns (some negative for losses)
        returns = [0.10, -0.05, 0.08, -0.12, 0.15, -0.03, 0.20, -0.08, 0.05]
        var_95 = calculate_var(returns, confidence_level=0.95)

        assert var_95 is not None
        assert var_95 > 0  # VaR should be positive (representing loss)

        # Test edge cases
        assert calculate_var([]) is None

    def test_portfolio_beta_calculation(self):
        """Test portfolio beta calculation."""

        def calculate_beta(asset_returns, market_returns):
            """Calculate beta coefficient.

            Formula: Beta = Covariance(Asset, Market) / Variance(Market)
            """
            if (
                len(asset_returns) != len(market_returns)
                or len(asset_returns) < 2
            ):
                return None

            n = len(asset_returns)
            asset_mean = sum(asset_returns) / n
            market_mean = sum(market_returns) / n

            # Calculate covariance
            covariance = sum(
                (asset_returns[i] - asset_mean)
                * (market_returns[i] - market_mean)
                for i in range(n)
            ) / (n - 1)

            # Calculate market variance
            market_variance = sum(
                (market_returns[i] - market_mean) ** 2 for i in range(n)
            ) / (n - 1)

            if market_variance == 0:
                return None

            return covariance / market_variance

        # Test beta calculation
        asset_returns = [0.10, 0.15, 0.05, 0.20, 0.12]
        market_returns = [0.08, 0.12, 0.04, 0.15, 0.10]

        beta = calculate_beta(asset_returns, market_returns)
        assert beta is not None
        assert beta > 0  # Should be positive for correlated assets

        # Test edge cases
        assert calculate_beta([], []) is None
        assert calculate_beta([0.1], [0.1]) is None
        assert calculate_beta([0.1, 0.2], [0.1]) is None  # Different lengths


class TestPortfolioMath:
    """Test portfolio mathematical calculations."""

    def test_portfolio_weighted_return(self):
        """Test weighted portfolio return calculation."""

        def calculate_weighted_return(weights, returns):
            """Calculate portfolio weighted return.

            Formula: Portfolio Return = Σ(Weight_i × Return_i)
            """
            if len(weights) != len(returns):
                return None

            if abs(sum(weights) - 1.0) > 0.001:  # Weights should sum to 1
                return None

            return sum(w * r for w, r in zip(weights, returns))

        # Test balanced portfolio
        weights = [0.4, 0.3, 0.2, 0.1]
        returns = [0.10, 0.15, 0.08, 0.20]

        portfolio_return = calculate_weighted_return(weights, returns)
        expected = 0.4 * 0.10 + 0.3 * 0.15 + 0.2 * 0.08 + 0.1 * 0.20

        assert abs(portfolio_return - expected) < 0.001

        # Test edge cases
        assert (
            calculate_weighted_return([0.5, 0.5], [0.1]) is None
        )  # Different lengths
        assert (
            calculate_weighted_return([0.6, 0.5], [0.1, 0.2]) is None
        )  # Weights don't sum to 1

    def test_portfolio_rebalancing(self):
        """Test portfolio rebalancing calculations."""

        def calculate_rebalancing_trades(
            current_values, target_weights, total_value
        ):
            """Calculate trades needed to rebalance portfolio.

            Returns dictionary of trades needed (positive = buy, negative = sell).
            """
            if len(current_values) != len(target_weights):
                return None

            if abs(sum(target_weights) - 1.0) > 0.001:
                return None

            trades = {}
            for i, (current, target_weight) in enumerate(
                zip(current_values, target_weights)
            ):
                target_value = total_value * target_weight
                trade_amount = target_value - current
                trades[f"asset_{i}"] = trade_amount

            return trades

        # Test rebalancing calculation
        current_values = [40000, 35000, 25000]  # Total: 100,000
        target_weights = [0.5, 0.3, 0.2]
        total_value = 100000

        trades = calculate_rebalancing_trades(
            current_values, target_weights, total_value
        )

        assert trades is not None
        # Asset 0: target 50,000 - current 40,000 = need to buy 10,000
        assert abs(trades["asset_0"] - 10000) < 0.01
        # Asset 1: target 30,000 - current 35,000 = need to sell 5,000
        assert abs(trades["asset_1"] - (-5000)) < 0.01


class TestRiskMetrics:
    """Test risk calculation functions."""

    def test_maximum_drawdown(self):
        """Test maximum drawdown calculation."""

        def calculate_max_drawdown(values):
            """Calculate maximum drawdown from peak to trough.

            Formula: Max DD = (Trough Value - Peak Value) / Peak Value
            """
            if len(values) < 2:
                return None

            max_dd = 0
            peak = values[0]

            for value in values[1:]:
                if value > peak:
                    peak = value
                else:
                    drawdown = (peak - value) / peak
                    max_dd = max(max_dd, drawdown)

            return max_dd

        # Test with portfolio values that have a drawdown
        portfolio_values = [
            100000,
            110000,
            115000,
            105000,
            95000,
            102000,
            120000,
        ]
        max_dd = calculate_max_drawdown(portfolio_values)

        assert max_dd is not None
        # Peak was 115,000, trough was 95,000
        expected_dd = (115000 - 95000) / 115000
        assert abs(max_dd - expected_dd) < 0.001

    def test_downside_deviation(self):
        """Test downside deviation calculation."""

        def calculate_downside_deviation(returns, target_return=0.0):
            """Calculate downside deviation (downside risk measure).

            Only considers returns below the target return.
            """
            downside_returns = [r for r in returns if r < target_return]

            if not downside_returns:
                return 0

            variance = sum(
                (r - target_return) ** 2 for r in downside_returns
            ) / len(downside_returns)
            return variance**0.5

        # Test with mixed returns
        returns = [0.10, -0.05, 0.08, -0.12, 0.15, -0.03, 0.20]
        downside_dev = calculate_downside_deviation(returns, target_return=0.0)

        assert downside_dev > 0
        # Should only consider negative returns
        negative_returns = [-0.05, -0.12, -0.03]
        expected_variance = sum(r**2 for r in negative_returns) / len(
            negative_returns
        )
        expected_dd = expected_variance**0.5

        assert abs(downside_dev - expected_dd) < 0.001


class TestDateUtilities:
    """Test date and time utility functions."""

    def test_business_days_calculation(self):
        """Test business days calculation."""

        def count_business_days(start_date, end_date):
            """Count business days between two dates."""
            if start_date > end_date:
                return 0

            current = start_date
            business_days = 0

            while current <= end_date:
                # Monday = 0, Sunday = 6
                if current.weekday() < 5:  # Monday to Friday
                    business_days += 1
                current += timedelta(days=1)

            return business_days

        # Test business days in a week
        monday = date(2024, 1, 15)  # Assuming this is a Monday
        friday = date(2024, 1, 19)

        bdays = count_business_days(monday, friday)
        assert bdays == 5  # Monday through Friday

        # Test including weekend
        sunday = date(2024, 1, 21)
        bdays_with_weekend = count_business_days(monday, sunday)
        assert bdays_with_weekend == 5  # Still only 5 business days

    def test_annualized_return_calculation(self):
        """Test annualized return calculation."""

        def annualize_return(total_return, days):
            """Convert total return to annualized return."""
            if days <= 0:
                return None

            years = days / 365.25  # Account for leap years
            if years == 0:
                return None

            return (1 + total_return) ** (1 / years) - 1

        # Test 6-month return
        total_return = 0.05  # 5% total return
        days = 180  # 6 months

        annualized = annualize_return(total_return, days)
        assert annualized is not None
        assert annualized > total_return  # Should be higher when annualized


class TestDecimalPrecision:
    """Test decimal precision handling for financial calculations."""

    def test_decimal_arithmetic_precision(self):
        """Test that decimal arithmetic maintains precision."""

        # Use Decimal for financial calculations
        price = Decimal("150.25")
        quantity = Decimal("100.5")

        total = price * quantity
        expected = Decimal("15100.125")

        assert total == expected
        assert isinstance(total, Decimal)

    def test_rounding_for_currency(self):
        """Test proper rounding for currency values."""

        def round_currency(value):
            """Round to 2 decimal places for currency."""
            return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Test rounding
        value = Decimal("123.456789")
        rounded = round_currency(value)

        assert rounded == Decimal("123.46")
        assert len(str(rounded).split(".")[-1]) <= 2

    def test_percentage_calculations(self):
        """Test percentage calculations with proper precision."""

        def calculate_percentage_change(old_value, new_value):
            """Calculate percentage change with proper precision."""
            if old_value == 0:
                return None

            change = ((new_value - old_value) / old_value) * 100
            return change.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        old_price = Decimal("100.00")
        new_price = Decimal("105.50")

        pct_change = calculate_percentage_change(old_price, new_price)
        assert pct_change == Decimal("5.50")


class TestDataValidation:
    """Test data validation and error handling."""

    def test_positive_number_validation(self):
        """Test validation for positive numbers."""

        def validate_positive(value, field_name="value"):
            """Validate that a value is positive."""
            if value is None:
                raise ValueError(f"{field_name} cannot be None")
            if value <= 0:
                raise ValueError(f"{field_name} must be positive")
            return True

        # Test valid positive number
        assert validate_positive(Decimal("100.50")) is True

        # Test invalid values
        with pytest.raises(ValueError, match="must be positive"):
            validate_positive(Decimal("-10.00"))

        with pytest.raises(ValueError, match="must be positive"):
            validate_positive(Decimal("0.00"))

        with pytest.raises(ValueError, match="cannot be None"):
            validate_positive(None)

    def test_percentage_range_validation(self):
        """Test validation for percentage values."""

        def validate_percentage(value, min_pct=0, max_pct=100):
            """Validate percentage is within range."""
            if value is None:
                raise ValueError("Percentage cannot be None")
            if value < min_pct or value > max_pct:
                raise ValueError(
                    f"Percentage must be between {min_pct}% and {max_pct}%"
                )
            return True

        # Test valid percentages
        assert validate_percentage(50.5) is True
        assert validate_percentage(0) is True
        assert validate_percentage(100) is True

        # Test invalid percentages
        with pytest.raises(ValueError, match="must be between"):
            validate_percentage(-5)

        with pytest.raises(ValueError, match="must be between"):
            validate_percentage(150)


class TestPerformanceMetrics:
    """Test performance measurement utilities."""

    def test_sortino_ratio_calculation(self):
        """Test Sortino ratio calculation."""

        def calculate_sortino_ratio(returns, target_return=0.0):
            """Calculate Sortino ratio (risk-adjusted return using downside deviation)."""
            if not returns:
                return None

            avg_return = sum(returns) / len(returns)

            # Calculate downside deviation
            downside_returns = [r for r in returns if r < target_return]
            if not downside_returns:
                return float("inf") if avg_return > target_return else None

            downside_variance = sum(
                (r - target_return) ** 2 for r in downside_returns
            ) / len(downside_returns)
            downside_deviation = downside_variance**0.5

            return (avg_return - target_return) / downside_deviation

        # Test with mixed returns
        returns = [0.10, -0.05, 0.15, -0.02, 0.20, 0.08, -0.10]
        sortino = calculate_sortino_ratio(returns)

        assert sortino is not None
        assert sortino > 0  # Should be positive for good performance

    def test_information_ratio_calculation(self):
        """Test Information ratio calculation."""

        def calculate_information_ratio(portfolio_returns, benchmark_returns):
            """Calculate Information ratio (excess return over benchmark per unit of tracking error)."""
            if (
                len(portfolio_returns) != len(benchmark_returns)
                or not portfolio_returns
            ):
                return None

            # Calculate excess returns
            excess_returns = [
                p - b for p, b in zip(portfolio_returns, benchmark_returns)
            ]

            avg_excess = sum(excess_returns) / len(excess_returns)

            # Calculate tracking error (standard deviation of excess returns)
            if len(excess_returns) < 2:
                return None

            variance = sum((e - avg_excess) ** 2 for e in excess_returns) / (
                len(excess_returns) - 1
            )
            tracking_error = variance**0.5

            if tracking_error == 0:
                return None

            return avg_excess / tracking_error

        # Test information ratio
        portfolio_returns = [0.12, 0.08, 0.15, 0.10, 0.18]
        benchmark_returns = [0.10, 0.06, 0.12, 0.08, 0.14]

        info_ratio = calculate_information_ratio(
            portfolio_returns, benchmark_returns
        )
        assert info_ratio is not None
        assert info_ratio > 0  # Portfolio outperforming benchmark
