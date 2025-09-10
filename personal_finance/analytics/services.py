"""Quantitative analytics and performance calculation services.

This module provides comprehensive analytical tools for portfolio and asset
performance analysis, including risk metrics, technical indicators, and
statistical calculations following modern portfolio theory principles.
"""

import logging
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, date, timedelta

import pandas as pd
import numpy as np
from django.db.models import QuerySet
from django.utils import timezone

from personal_finance.assets.models import Asset

# Graceful import handling for missing models
try:
    from personal_finance.assets.models import PriceHistory
except ImportError:
    PriceHistory = None

try:
    from personal_finance.portfolios.models import Portfolio, Position, PortfolioSnapshot
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
    
    def calculate_portfolio_metrics(self, 
                                  portfolio: Portfolio, 
                                  start_date: date,
                                  end_date: date) -> Dict[str, Union[float, None]]:
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
                snapshot_date__lte=end_date
            ).order_by('snapshot_date')
            
            if len(snapshots) < 2:
                logger.warning(f"Insufficient data for portfolio {portfolio.id}")
                return self._empty_metrics()
            
            # Convert to pandas for efficient calculations
            df = pd.DataFrame([
                {
                    'date': snapshot.snapshot_date,
                    'value': float(snapshot.total_value),
                    'cost_basis': float(snapshot.total_cost_basis)
                }
                for snapshot in snapshots
            ])
            df.set_index('date', inplace=True)
            
            # Calculate daily returns
            df['returns'] = df['value'].pct_change().dropna()
            
            if len(df['returns']) < 2:
                return self._empty_metrics()
            
            # Basic metrics
            total_return = (df['value'].iloc[-1] / df['value'].iloc[0] - 1) * 100
            
            # Annualized metrics
            days = (end_date - start_date).days
            years = days / 365.25
            
            if years > 0:
                annualized_return = ((df['value'].iloc[-1] / df['value'].iloc[0]) ** (1/years) - 1) * 100
                annualized_volatility = df['returns'].std() * np.sqrt(252) * 100  # 252 trading days
            else:
                annualized_return = None
                annualized_volatility = None
            
            # Risk-adjusted metrics
            excess_returns = df['returns'] - (self.risk_free_rate / 252)  # Daily risk-free rate
            sharpe_ratio = (excess_returns.mean() / df['returns'].std() * np.sqrt(252)) if df['returns'].std() != 0 else None
            
            # Downside metrics
            negative_returns = df['returns'][df['returns'] < 0]
            downside_deviation = negative_returns.std() * np.sqrt(252) if len(negative_returns) > 0 else 0
            sortino_ratio = (excess_returns.mean() / downside_deviation * np.sqrt(252)) if downside_deviation != 0 else None
            
            # Drawdown analysis
            cumulative_returns = (1 + df['returns']).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdowns = (cumulative_returns - running_max) / running_max
            max_drawdown = abs(drawdowns.min()) * 100
            
            # Calmar ratio
            calmar_ratio = (annualized_return / max_drawdown) if max_drawdown != 0 and annualized_return else None
            
            # Value at Risk (95% confidence)
            var_95 = np.percentile(df['returns'], 5) * 100
            
            return {
                'total_return': total_return,
                'annualized_return': annualized_return,
                'volatility': annualized_volatility,
                'sharpe_ratio': sharpe_ratio,
                'sortino_ratio': sortino_ratio,
                'max_drawdown': max_drawdown,
                'calmar_ratio': calmar_ratio,
                'value_at_risk': var_95,
                'beta': None,  # Would need benchmark data
                'start_value': float(df['value'].iloc[0]),
                'end_value': float(df['value'].iloc[-1]),
                'analysis_period_days': days,
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {e}")
            return self._empty_metrics()
    
    def calculate_asset_correlation_matrix(self, 
                                         assets: List[Asset], 
                                         start_date: date,
                                         end_date: date) -> Optional[pd.DataFrame]:
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
                prices = PriceHistory.objects.filter(
                    asset=asset,
                    date__gte=start_date,
                    date__lte=end_date
                ).order_by('date').values_list('date', 'close_price')
                
                if len(prices) >= 30:  # Minimum 30 days of data
                    price_data[asset.symbol] = pd.Series(
                        [float(price[1]) for price in prices],
                        index=[price[0] for price in prices]
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
            logger.error(f"Error calculating correlation matrix: {e}")
            return None
    
    def calculate_portfolio_allocation(self, portfolio: Portfolio) -> Dict[str, Dict[str, float]]:
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
                portfolio=portfolio,
                is_active=True
            ).select_related('asset')
            
            if not positions:
                return {
                    'asset_type': {},
                    'sector': {},
                    'currency': {},
                    'individual_assets': {}
                }
            
            total_value = sum(pos.current_value for pos in positions)
            
            if total_value == 0:
                return {
                    'asset_type': {},
                    'sector': {},
                    'currency': {},
                    'individual_assets': {}
                }
            
            # Calculate allocations
            allocations = {
                'asset_type': {},
                'sector': {},
                'currency': {},
                'individual_assets': {}
            }
            
            for position in positions:
                weight = float(position.current_value / total_value * 100)
                
                # Asset type allocation
                asset_type = position.asset.asset_type
                allocations['asset_type'][asset_type] = allocations['asset_type'].get(asset_type, 0) + weight
                
                # Sector allocation (for stocks)
                if position.asset.sector:
                    sector = position.asset.sector
                    allocations['sector'][sector] = allocations['sector'].get(sector, 0) + weight
                
                # Currency allocation
                currency = position.asset.currency
                allocations['currency'][currency] = allocations['currency'].get(currency, 0) + weight
                
                # Individual asset allocation
                symbol = position.asset.symbol
                allocations['individual_assets'][symbol] = weight
            
            return allocations
            
        except Exception as e:
            logger.error(f"Error calculating portfolio allocation: {e}")
            return {
                'asset_type': {},
                'sector': {},
                'currency': {},
                'individual_assets': {}
            }
    
    def _empty_metrics(self) -> Dict[str, None]:
        """Return empty metrics dictionary."""
        return {
            'total_return': None,
            'annualized_return': None,
            'volatility': None,
            'sharpe_ratio': None,
            'sortino_ratio': None,
            'max_drawdown': None,
            'calmar_ratio': None,
            'value_at_risk': None,
            'beta': None,
            'start_value': None,
            'end_value': None,
            'analysis_period_days': None,
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
    def bollinger_bands(prices: pd.Series, 
                       window: int = 20, 
                       num_std: float = 2) -> Dict[str, pd.Series]:
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
        
        return {
            'upper': upper,
            'middle': middle,
            'lower': lower
        }
    
    @staticmethod
    def macd(prices: pd.Series, 
             fast: int = 12, 
             slow: int = 26, 
             signal: int = 9) -> Dict[str, pd.Series]:
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
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }


class RiskAnalytics:
    """Risk analysis and measurement tools.
    
    Provides various risk metrics and analysis tools for portfolio
    and individual asset risk assessment.
    """
    
    @staticmethod
    def value_at_risk(returns: pd.Series, 
                     confidence_level: float = 0.95) -> float:
        """Calculate Value at Risk.
        
        Args:
            returns: Return series
            confidence_level: Confidence level (default 95%)
            
        Returns:
            VaR value as percentage
        """
        return np.percentile(returns, (1 - confidence_level) * 100)
    
    @staticmethod
    def expected_shortfall(returns: pd.Series, 
                          confidence_level: float = 0.95) -> float:
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
    def maximum_drawdown(cumulative_returns: pd.Series) -> Tuple[float, date, date]:
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