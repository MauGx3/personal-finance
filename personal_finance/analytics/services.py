"""Quantitative analytics and performance calculation services.

This module provides comprehensive analytical tools for portfolio and asset
performance analysis, including risk metrics, technical indicators, and
statistical calculations following modern portfolio theory principles.
"""

import logging
from typing import Dict, List, Optional, Tuple, Union
from datetime import date

import pandas as pd
import numpy as np

from personal_finance.assets.models import Asset

# Graceful import handling for missing models
try:
    from personal_finance.assets.models import PriceHistory
except ImportError:
    PriceHistory = None

try:
    from personal_finance.portfolios.models import (
        Portfolio,
        Position,
        PortfolioSnapshot,
    )
except ImportError:
    Portfolio = Position = PortfolioSnapshot = None

logger = logging.getLogger(__name__)


class PerformanceAnalytics:
    """Core performance analytics engine for portfolios and assets.

    Provides comprehensive performance analysis including returns, volatility,
    risk-adjusted metrics, and benchmark comparisons following industry standards.
    """

    def __init__(self, risk_free_rate: float = 0.02):
        """Initialize analytics with risk-free rate assumption.

        Args:
            risk_free_rate: Annual risk-free rate for Sharpe ratio calculations.
        """
        self.risk_free_rate = risk_free_rate

    def calculate_portfolio_metrics(
        self, portfolio: Portfolio, start_date: date, end_date: date
    ) -> Dict[str, Union[float, None]]:
        """Calculate comprehensive portfolio performance metrics.

        Args:
            portfolio: Portfolio instance to analyze
            start_date: Analysis start date
            end_date: Analysis end date

        Returns:
            Dictionary containing performance metrics:
            - total_return: Absolute return percentage
            - annualized_return: Annualized return percentage
            - volatility: Annualized volatility (standard deviation)
            - sharpe_ratio: Risk-adjusted return metric
            - max_drawdown: Maximum peak-to-trough decline
            - calmar_ratio: Return/max drawdown ratio
            - sortino_ratio: Downside deviation adjusted return
            - beta: Market beta (if benchmark provided)
            - value_at_risk: 95% Value at Risk

        Example:
            >>> analytics = PerformanceAnalytics()
            >>> metrics = analytics.calculate_portfolio_metrics(
            ...     portfolio,
            ...     date(2024, 1, 1),
            ...     date(2024, 12, 31)
            ... )
            >>> print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        """
        try:
            # Get historical snapshots for the period
            snapshots = PortfolioSnapshot.objects.filter(
                portfolio=portfolio,
                snapshot_date__gte=start_date,
                snapshot_date__lte=end_date,
            ).order_by("snapshot_date")

            if len(snapshots) < 2:
                logger.warning(
                    f"Insufficient data for portfolio {portfolio.id}"
                )
                return self._empty_metrics()

            # Convert to pandas for efficient calculations
            df = pd.DataFrame(
                [
                    {
                        "date": snapshot.snapshot_date,
                        "value": float(snapshot.total_value),
                        "cost_basis": float(snapshot.total_cost_basis),
                    }
                    for snapshot in snapshots
                ]
            )
            df.set_index("date", inplace=True)

            # Calculate daily returns
            df["returns"] = df["value"].pct_change().dropna()

            if len(df["returns"]) < 2:
                return self._empty_metrics()

            # Basic metrics
            total_return = (
                df["value"].iloc[-1] / df["value"].iloc[0] - 1
            ) * 100

            # Annualized metrics
            days = (end_date - start_date).days
            years = days / 365.25

            if years > 0:
                annualized_return = (
                    (df["value"].iloc[-1] / df["value"].iloc[0]) ** (1 / years)
                    - 1
                ) * 100
                annualized_volatility = (
                    df["returns"].std() * np.sqrt(252) * 100
                )  # 252 trading days
            else:
                annualized_return = None
                annualized_volatility = None

            # Risk-adjusted metrics
            excess_returns = df["returns"] - (
                self.risk_free_rate / 252
            )  # Daily risk-free rate
            sharpe_ratio = (
                (excess_returns.mean() / df["returns"].std() * np.sqrt(252))
                if df["returns"].std() != 0
                else None
            )

            # Downside metrics
            negative_returns = df["returns"][df["returns"] < 0]
            downside_deviation = (
                negative_returns.std() * np.sqrt(252)
                if len(negative_returns) > 0
                else 0
            )
            sortino_ratio = (
                (excess_returns.mean() / downside_deviation * np.sqrt(252))
                if downside_deviation != 0
                else None
            )

            # Drawdown analysis
            cumulative_returns = (1 + df["returns"]).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdowns = (cumulative_returns - running_max) / running_max
            max_drawdown = abs(drawdowns.min()) * 100

            # Calmar ratio
            calmar_ratio = (
                (annualized_return / max_drawdown)
                if max_drawdown != 0 and annualized_return
                else None
            )

            # Value at Risk (95% confidence)
            var_95 = np.percentile(df["returns"], 5) * 100

            return {
                "total_return": total_return,
                "annualized_return": annualized_return,
                "volatility": annualized_volatility,
                "sharpe_ratio": sharpe_ratio,
                "sortino_ratio": sortino_ratio,
                "max_drawdown": max_drawdown,
                "calmar_ratio": calmar_ratio,
                "value_at_risk": var_95,
                "beta": None,  # Would need benchmark data
                "start_value": float(df["value"].iloc[0]),
                "end_value": float(df["value"].iloc[-1]),
                "analysis_period_days": days,
            }

        except Exception as e:
            logger.error("Error calculating portfolio metrics: %s", e)
            return self._empty_metrics()

    @staticmethod
    def calculate_asset_correlation_matrix(
        assets: List[Asset], start_date: date, end_date: date
    ) -> Optional[pd.DataFrame]:
        """Calculate correlation matrix for a list of assets.

        Args:
            assets: List of Asset instances
            start_date: Analysis start date
            end_date: Analysis end date

        Returns:
            Pandas DataFrame with correlation matrix or None if insufficient data.
        """
        try:
            # Collect price data for all assets
            price_data = {}

            for asset in assets:
                prices = (
                    PriceHistory.objects.filter(
                        asset=asset, date__gte=start_date, date__lte=end_date
                    )
                    .order_by("date")
                    .values_list("date", "close_price")
                )

                if len(prices) >= 30:  # Minimum 30 days of data
                    price_data[asset.symbol] = pd.Series(
                        [float(price[1]) for price in prices],
                        index=[price[0] for price in prices],
                    )

            if len(price_data) < 2:
                return None

            # Create DataFrame and calculate returns
            df = pd.DataFrame(price_data)
            returns = df.pct_change().dropna()

            # Calculate correlation matrix
            correlation_matrix = returns.corr()

            return correlation_matrix

        except Exception as e:
            logger.error("Error calculating correlation matrix: %s", e)
            return None

    @staticmethod
    def calculate_portfolio_allocation(
        portfolio: Portfolio,
    ) -> Dict[str, Dict[str, float]]:
        """Calculate portfolio allocation by various dimensions.

        Args:
            portfolio: Portfolio instance to analyze

        Returns:
            Dictionary containing allocations by:
            - asset_type: Percentage allocation by asset type
            - sector: Percentage allocation by sector (for stocks)
            - currency: Percentage allocation by currency
            - individual_assets: Percentage allocation by individual assets
        """
        try:
            positions = Position.objects.filter(
                portfolio=portfolio, is_active=True
            ).select_related("asset")

            if not positions:
                return {
                    "asset_type": {},
                    "sector": {},
                    "currency": {},
                    "individual_assets": {},
                }

            total_value = sum(pos.current_value for pos in positions)

            if total_value == 0:
                return {
                    "asset_type": {},
                    "sector": {},
                    "currency": {},
                    "individual_assets": {},
                }

            # Calculate allocations
            allocations = {
                "asset_type": {},
                "sector": {},
                "currency": {},
                "individual_assets": {},
            }

            for position in positions:
                weight = float(position.current_value / total_value * 100)

                # Asset type allocation
                asset_type = position.asset.asset_type
                allocations["asset_type"][asset_type] = (
                    allocations["asset_type"].get(asset_type, 0) + weight
                )

                # Sector allocation (for stocks)
                if position.asset.sector:
                    sector = position.asset.sector
                    allocations["sector"][sector] = (
                        allocations["sector"].get(sector, 0) + weight
                    )

                # Currency allocation
                currency = position.asset.currency
                allocations["currency"][currency] = (
                    allocations["currency"].get(currency, 0) + weight
                )

                # Individual asset allocation
                symbol = position.asset.symbol
                allocations["individual_assets"][symbol] = weight

            return allocations

        except Exception as e:
            logger.error("Error calculating portfolio allocation: %s", e)
            return {
                "asset_type": {},
                "sector": {},
                "currency": {},
                "individual_assets": {},
            }

    @staticmethod
    def _empty_metrics() -> Dict[str, None]:
        """Return empty metrics dictionary."""
        return {
            "total_return": None,
            "annualized_return": None,
            "volatility": None,
            "sharpe_ratio": None,
            "sortino_ratio": None,
            "max_drawdown": None,
            "calmar_ratio": None,
            "value_at_risk": None,
            "beta": None,
            "start_value": None,
            "end_value": None,
            "analysis_period_days": None,
        }


class TechnicalIndicators:
    """Technical analysis indicators for asset price analysis.

    Provides commonly used technical indicators for chartist analysis
    and algorithmic trading strategies.
    """

    @staticmethod
    def moving_average(prices: pd.Series, window: int) -> pd.Series:
        """Calculate simple moving average.

        Args:
            prices: Price series
            window: Number of periods for moving average

        Returns:
            Moving average series
        """
        return prices.rolling(window=window).mean()

    @staticmethod
    def exponential_moving_average(prices: pd.Series, span: int) -> pd.Series:
        """Calculate exponential moving average.

        Args:
            prices: Price series
            span: Span for EMA calculation

        Returns:
            Exponential moving average series
        """
        return prices.ewm(span=span).mean()

    @staticmethod
    def rsi(prices: pd.Series, window: int = 14) -> pd.Series:
        """Calculate Relative Strength Index.

        Args:
            prices: Price series
            window: RSI calculation window (default 14)

        Returns:
            RSI series (0-100 scale)
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def bollinger_bands(
        prices: pd.Series, window: int = 20, num_std: float = 2
    ) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands.

        Args:
            prices: Price series
            window: Moving average window (default 20)
            num_std: Number of standard deviations (default 2)

        Returns:
            Dictionary with 'upper', 'middle', 'lower' band series
        """
        middle = prices.rolling(window=window).mean()
        std = prices.rolling(window=window).std()

        upper = middle + (std * num_std)
        lower = middle - (std * num_std)

        return {"upper": upper, "middle": middle, "lower": lower}

    @staticmethod
    def macd(
        prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Dict[str, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence).

        Args:
            prices: Price series
            fast: Fast EMA period (default 12)
            slow: Slow EMA period (default 26)
            signal: Signal line EMA period (default 9)

        Returns:
            Dictionary with 'macd', 'signal', 'histogram' series
        """
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()

        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line

        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram,
        }

    @staticmethod
    def stochastic_oscillator(
        high: pd.Series, low: pd.Series, close: pd.Series, k_period: int = 14, d_period: int = 3
    ) -> Dict[str, pd.Series]:
        """Calculate Stochastic Oscillator.

        Args:
            high: High price series
            low: Low price series
            close: Close price series
            k_period: %K period (default 14)
            d_period: %D smoothing period (default 3)

        Returns:
            Dictionary with '%K' and '%D' series
        """
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return {
            "%K": k_percent,
            "%D": d_percent,
        }

    @staticmethod
    def williams_r(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Williams %R.

        Args:
            high: High price series
            low: Low price series
            close: Close price series
            period: Calculation period (default 14)

        Returns:
            Williams %R series
        """
        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()
        
        williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
        
        return williams_r

    @staticmethod
    def commodity_channel_index(
        high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20
    ) -> pd.Series:
        """Calculate Commodity Channel Index (CCI).

        Args:
            high: High price series
            low: Low price series
            close: Close price series
            period: Calculation period (default 20)

        Returns:
            CCI series
        """
        typical_price = (high + low + close) / 3
        sma_tp = typical_price.rolling(window=period).mean()
        mean_deviation = typical_price.rolling(window=period).apply(
            lambda x: np.mean(np.abs(x - x.mean())), raw=False
        )
        
        cci = (typical_price - sma_tp) / (0.015 * mean_deviation)
        
        return cci

    @staticmethod
    def average_true_range(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Average True Range (ATR).

        Args:
            high: High price series
            low: Low price series
            close: Close price series
            period: Calculation period (default 14)

        Returns:
            ATR series
        """
        prev_close = close.shift(1)
        
        tr1 = high - low
        tr2 = np.abs(high - prev_close)
        tr3 = np.abs(low - prev_close)
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr

    @staticmethod
    def parabolic_sar(
        high: pd.Series, low: pd.Series, acceleration: float = 0.02, maximum: float = 0.2
    ) -> pd.Series:
        """Calculate Parabolic SAR.

        Args:
            high: High price series
            low: Low price series
            acceleration: Acceleration factor (default 0.02)
            maximum: Maximum acceleration (default 0.2)

        Returns:
            Parabolic SAR series
        """
        # Simplified implementation - full implementation would be more complex
        length = len(high)
        sar = pd.Series(index=high.index, dtype=float)
        trend = pd.Series(index=high.index, dtype=int)
        
        # Initialize
        sar.iloc[0] = low.iloc[0]
        trend.iloc[0] = 1
        
        for i in range(1, length):
            if trend.iloc[i-1] == 1:  # Uptrend
                sar.iloc[i] = sar.iloc[i-1] + acceleration * (high.iloc[i-1] - sar.iloc[i-1])
                if low.iloc[i] <= sar.iloc[i]:
                    sar.iloc[i] = high.iloc[i-1]
                    trend.iloc[i] = -1
                else:
                    trend.iloc[i] = 1
            else:  # Downtrend
                sar.iloc[i] = sar.iloc[i-1] + acceleration * (low.iloc[i-1] - sar.iloc[i-1])
                if high.iloc[i] >= sar.iloc[i]:
                    sar.iloc[i] = low.iloc[i-1]
                    trend.iloc[i] = 1
                else:
                    trend.iloc[i] = -1
        
        return sar

    @staticmethod
    def volume_weighted_average_price(
        high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series
    ) -> pd.Series:
        """Calculate Volume Weighted Average Price (VWAP).

        Args:
            high: High price series
            low: Low price series
            close: Close price series
            volume: Volume series

        Returns:
            VWAP series
        """
        typical_price = (high + low + close) / 3
        cumulative_volume = volume.cumsum()
        cumulative_pv = (typical_price * volume).cumsum()
        
        vwap = cumulative_pv / cumulative_volume
        
        return vwap

    @staticmethod
    def on_balance_volume(close: pd.Series, volume: pd.Series) -> pd.Series:
        """Calculate On Balance Volume (OBV).

        Args:
            close: Close price series
            volume: Volume series

        Returns:
            OBV series
        """
        price_change = close.diff()
        obv = pd.Series(index=close.index, dtype=float)
        obv.iloc[0] = volume.iloc[0]
        
        for i in range(1, len(close)):
            if price_change.iloc[i] > 0:
                obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
            elif price_change.iloc[i] < 0:
                obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        
        return obv

    @staticmethod
    def money_flow_index(
        high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series, period: int = 14
    ) -> pd.Series:
        """Calculate Money Flow Index (MFI).

        Args:
            high: High price series
            low: Low price series
            close: Close price series
            volume: Volume series
            period: Calculation period (default 14)

        Returns:
            MFI series
        """
        typical_price = (high + low + close) / 3
        money_flow = typical_price * volume
        
        price_change = typical_price.diff()
        
        positive_flow = pd.Series(index=close.index, dtype=float)
        negative_flow = pd.Series(index=close.index, dtype=float)
        
        positive_flow = money_flow.where(price_change > 0, 0).rolling(window=period).sum()
        negative_flow = money_flow.where(price_change < 0, 0).rolling(window=period).sum()
        
        money_flow_ratio = positive_flow / negative_flow
        mfi = 100 - (100 / (1 + money_flow_ratio))
        
        return mfi

    @staticmethod
    def ichimoku_cloud(
        high: pd.Series, low: pd.Series, close: pd.Series,
        tenkan_period: int = 9, kijun_period: int = 26, senkou_span_b_period: int = 52
    ) -> Dict[str, pd.Series]:
        """Calculate Ichimoku Cloud components.

        Args:
            high: High price series
            low: Low price series
            close: Close price series
            tenkan_period: Tenkan-sen period (default 9)
            kijun_period: Kijun-sen period (default 26)
            senkou_span_b_period: Senkou Span B period (default 52)

        Returns:
            Dictionary with Ichimoku components
        """
        # Tenkan-sen (Conversion Line)
        tenkan_sen = (high.rolling(window=tenkan_period).max() + low.rolling(window=tenkan_period).min()) / 2
        
        # Kijun-sen (Base Line)
        kijun_sen = (high.rolling(window=kijun_period).max() + low.rolling(window=kijun_period).min()) / 2
        
        # Senkou Span A (Leading Span A)
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(kijun_period)
        
        # Senkou Span B (Leading Span B)
        senkou_span_b = ((high.rolling(window=senkou_span_b_period).max() + 
                         low.rolling(window=senkou_span_b_period).min()) / 2).shift(kijun_period)
        
        # Chikou Span (Lagging Span)
        chikou_span = close.shift(-kijun_period)
        
        return {
            "tenkan_sen": tenkan_sen,
            "kijun_sen": kijun_sen,
            "senkou_span_a": senkou_span_a,
            "senkou_span_b": senkou_span_b,
            "chikou_span": chikou_span,
        }


class RiskAnalytics:
    """Risk analysis and measurement tools.

    Provides various risk metrics and analysis tools for portfolio
    and individual asset risk assessment.
    """

    @staticmethod
    def value_at_risk(
        returns: pd.Series, confidence_level: float = 0.95
    ) -> float:
        """Calculate Value at Risk.

        Args:
            returns: Return series
            confidence_level: Confidence level (default 95%)

        Returns:
            VaR value as percentage
        """
        return np.percentile(returns, (1 - confidence_level) * 100)

    @staticmethod
    def expected_shortfall(
        returns: pd.Series, confidence_level: float = 0.95
    ) -> float:
        """Calculate Expected Shortfall (Conditional VaR).

        Args:
            returns: Return series
            confidence_level: Confidence level (default 95%)

        Returns:
            Expected shortfall as percentage
        """
        var = RiskAnalytics.value_at_risk(returns, confidence_level)
        return returns[returns <= var].mean()

    @staticmethod
    def maximum_drawdown(
        cumulative_returns: pd.Series,
    ) -> Tuple[float, date, date]:
        """Calculate maximum drawdown and its duration.

        Args:
            cumulative_returns: Cumulative return series

        Returns:
            Tuple of (max_drawdown_pct, start_date, end_date)
        """
        running_max = cumulative_returns.expanding().max()
        drawdowns = (cumulative_returns - running_max) / running_max

        max_dd = drawdowns.min()
        max_dd_end = drawdowns.idxmin()

        # Find start of drawdown period
        max_dd_start = cumulative_returns[:max_dd_end].idxmax()

        return abs(max_dd) * 100, max_dd_start, max_dd_end
