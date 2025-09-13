"""Polars integration for modern data analysis in personal finance platform.

This module provides high-performance data processing capabilities using Polars
DataFrame library as specified in the S.C.A.F.F. structure requirements.
Implements modern data analysis workflows for financial data.
"""

import logging
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date, timedelta
from dataclasses import dataclass

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False
    pl = None

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

try:
    from django.conf import settings
    from django.core.cache import cache
    from django.utils import timezone
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False
    # Create simple substitutes
    class MockCache:
        @staticmethod
        def get(key, default=None):
            return default
        @staticmethod
        def set(key, value, timeout=None):
            pass
    cache = MockCache()
    
    class MockTimezone:
        @staticmethod
        def now():
            return datetime.now()
    timezone = MockTimezone()
    
    class MockSettings:
        DEBUG = False
    settings = MockSettings()

logger = logging.getLogger(__name__)


class PolarsDataProcessor:
    """High-performance data processor using Polars DataFrame library.
    
    Provides efficient data processing capabilities for financial data analysis
    with lazy evaluation and optimized queries. Falls back to pandas if Polars
    is not available.
    """
    
    def __init__(self):
        """Initialize the data processor with available libraries."""
        self.polars_available = POLARS_AVAILABLE
        self.pandas_available = PANDAS_AVAILABLE
        
        if not (self.polars_available or self.pandas_available):
            raise ImportError(
                "Neither polars nor pandas is available. "
                "Install at least one: pip install polars pandas"
            )
        
        logger.info(
            f"PolarsDataProcessor initialized - "
            f"Polars: {self.polars_available}, Pandas: {self.pandas_available}"
        )
    
    def create_price_dataframe(self, price_data: List[Dict]) -> Union[pl.DataFrame, pd.DataFrame]:
        """Create a DataFrame from price data.
        
        Args:
            price_data: List of dictionaries containing price information
            
        Returns:
            Polars or Pandas DataFrame depending on availability
        """
        if not price_data:
            return self._create_empty_price_dataframe()
        
        if self.polars_available:
            return pl.DataFrame(price_data)
        elif self.pandas_available:
            return pd.DataFrame(price_data)
        else:
            raise RuntimeError("No DataFrame library available")
    
    def _create_empty_price_dataframe(self) -> Union[pl.DataFrame, pd.DataFrame]:
        """Create an empty DataFrame with price data schema."""
        schema = {
            'symbol': str,
            'date': str,  # Will be converted to date type
            'open_price': float,
            'high_price': float,
            'low_price': float,
            'close_price': float,
            'volume': int,
            'adjusted_close': float,
        }
        
        if self.polars_available:
            return pl.DataFrame(schema=schema)
        elif self.pandas_available:
            return pd.DataFrame(columns=list(schema.keys()))
        else:
            raise RuntimeError("No DataFrame library available")
    
    def calculate_moving_averages(self, 
                                 df: Union[pl.DataFrame, pd.DataFrame], 
                                 price_column: str = 'close_price',
                                 windows: List[int] = [20, 50, 200]) -> Union[pl.DataFrame, pd.DataFrame]:
        """Calculate moving averages for price data.
        
        Args:
            df: DataFrame containing price data
            price_column: Column name for price data
            windows: List of window sizes for moving averages
            
        Returns:
            DataFrame with additional moving average columns
        """
        if self.polars_available and isinstance(df, pl.DataFrame):
            return self._calculate_ma_polars(df, price_column, windows)
        elif self.pandas_available and isinstance(df, pd.DataFrame):
            return self._calculate_ma_pandas(df, price_column, windows)
        else:
            raise ValueError(f"Unsupported DataFrame type: {type(df)}")
    
    def _calculate_ma_polars(self, 
                            df: pl.DataFrame, 
                            price_column: str,
                            windows: List[int]) -> pl.DataFrame:
        """Calculate moving averages using Polars lazy evaluation."""
        lazy_df = df.lazy()
        
        # Add moving averages using Polars' efficient rolling window operations
        for window in windows:
            ma_column = f'ma_{window}'
            lazy_df = lazy_df.with_columns([
                pl.col(price_column).rolling_mean(window).alias(ma_column)
            ])
        
        return lazy_df.collect()
    
    def _calculate_ma_pandas(self, 
                            df: pd.DataFrame, 
                            price_column: str,
                            windows: List[int]) -> pd.DataFrame:
        """Calculate moving averages using Pandas."""
        result_df = df.copy()
        
        for window in windows:
            ma_column = f'ma_{window}'
            result_df[ma_column] = result_df[price_column].rolling(window=window).mean()
        
        return result_df
    
    def calculate_technical_indicators(self, 
                                     df: Union[pl.DataFrame, pd.DataFrame]) -> Union[pl.DataFrame, pd.DataFrame]:
        """Calculate common technical indicators.
        
        Args:
            df: DataFrame containing OHLCV data
            
        Returns:
            DataFrame with additional technical indicator columns
        """
        if self.polars_available and isinstance(df, pl.DataFrame):
            return self._calculate_indicators_polars(df)
        elif self.pandas_available and isinstance(df, pd.DataFrame):
            return self._calculate_indicators_pandas(df)
        else:
            raise ValueError(f"Unsupported DataFrame type: {type(df)}")
    
    def _calculate_indicators_polars(self, df: pl.DataFrame) -> pl.DataFrame:
        """Calculate technical indicators using Polars."""
        lazy_df = df.lazy()
        
        # RSI calculation using Polars
        lazy_df = lazy_df.with_columns([
            # Calculate price changes
            (pl.col('close_price') - pl.col('close_price').shift(1)).alias('price_change'),
        ])
        
        # Calculate gains and losses for RSI
        lazy_df = lazy_df.with_columns([
            pl.when(pl.col('price_change') > 0)
            .then(pl.col('price_change'))
            .otherwise(0)
            .alias('gain'),
            
            pl.when(pl.col('price_change') < 0)
            .then(-pl.col('price_change'))
            .otherwise(0)
            .alias('loss'),
        ])
        
        # Calculate RSI (14-period)
        lazy_df = lazy_df.with_columns([
            (100 - (100 / (1 + (
                pl.col('gain').rolling_mean(14) / pl.col('loss').rolling_mean(14)
            )))).alias('rsi_14')
        ])
        
        # Calculate Bollinger Bands
        lazy_df = lazy_df.with_columns([
            pl.col('close_price').rolling_mean(20).alias('bb_middle'),
            pl.col('close_price').rolling_std(20).alias('bb_std'),
        ])
        
        lazy_df = lazy_df.with_columns([
            (pl.col('bb_middle') + 2 * pl.col('bb_std')).alias('bb_upper'),
            (pl.col('bb_middle') - 2 * pl.col('bb_std')).alias('bb_lower'),
        ])
        
        return lazy_df.collect()
    
    def _calculate_indicators_pandas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators using Pandas."""
        result_df = df.copy()
        
        # Calculate price changes
        result_df['price_change'] = result_df['close_price'].diff()
        
        # Calculate RSI
        gain = result_df['price_change'].where(result_df['price_change'] > 0, 0)
        loss = -result_df['price_change'].where(result_df['price_change'] < 0, 0)
        
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        
        rs = avg_gain / avg_loss
        result_df['rsi_14'] = 100 - (100 / (1 + rs))
        
        # Calculate Bollinger Bands
        result_df['bb_middle'] = result_df['close_price'].rolling(window=20).mean()
        result_df['bb_std'] = result_df['close_price'].rolling(window=20).std()
        result_df['bb_upper'] = result_df['bb_middle'] + 2 * result_df['bb_std']
        result_df['bb_lower'] = result_df['bb_middle'] - 2 * result_df['bb_std']
        
        return result_df
    
    def calculate_advanced_technical_indicators(self, 
                                           df: Union[pl.DataFrame, pd.DataFrame],
                                           indicators: List[str] = None) -> Union[pl.DataFrame, pd.DataFrame]:
        """Calculate advanced technical indicators using modern libraries.
        
        Args:
            df: DataFrame containing price data
            indicators: List of indicators to calculate
            
        Returns:
            DataFrame with additional technical indicators
        """
        if indicators is None:
            indicators = ['macd', 'stochastic', 'williams_r', 'atr']
        
        try:
            if self.polars_available and isinstance(df, pl.DataFrame):
                return self._calculate_advanced_indicators_polars(df, indicators)
            elif self.pandas_available and isinstance(df, pd.DataFrame):
                return self._calculate_advanced_indicators_pandas(df, indicators)
            else:
                return df
                
        except Exception as e:
            logger.error(f"Error calculating advanced technical indicators: {e}")
            return df
    
    def _calculate_advanced_indicators_polars(self, df: pl.DataFrame, indicators: List[str]) -> pl.DataFrame:
        """Calculate advanced indicators using Polars."""
        result_df = df.clone()
        
        if 'close_price' not in df.columns:
            return result_df
        
        try:
            # MACD (Moving Average Convergence Divergence)
            if 'macd' in indicators:
                ema_12 = pl.col('close_price').ewm_mean(span=12)
                ema_26 = pl.col('close_price').ewm_mean(span=26)
                macd_line = ema_12 - ema_26
                signal_line = macd_line.ewm_mean(span=9)
                
                result_df = result_df.with_columns([
                    macd_line.alias('macd'),
                    signal_line.alias('macd_signal'),
                    (macd_line - signal_line).alias('macd_histogram')
                ])
            
            # Average True Range (ATR)
            if 'atr' in indicators and all(col in df.columns for col in ['high_price', 'low_price']):
                high_low = pl.col('high_price') - pl.col('low_price')
                high_close = (pl.col('high_price') - pl.col('close_price').shift(1)).abs()
                low_close = (pl.col('low_price') - pl.col('close_price').shift(1)).abs()
                
                true_range = pl.max_horizontal([high_low, high_close, low_close])
                atr = true_range.rolling_mean(window_size=14)
                
                result_df = result_df.with_columns([
                    true_range.alias('true_range'),
                    atr.alias('atr_14')
                ])
            
            # Williams %R
            if 'williams_r' in indicators and all(col in df.columns for col in ['high_price', 'low_price']):
                highest_high = pl.col('high_price').rolling_max(window=14)
                lowest_low = pl.col('low_price').rolling_min(window=14)
                williams_r = (highest_high - pl.col('close_price')) / (highest_high - lowest_low) * -100
                
                result_df = result_df.with_columns([
                    williams_r.alias('williams_r_14')
                ])
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error in Polars advanced indicators: {e}")
            return result_df
    
    def _calculate_advanced_indicators_pandas(self, df: pd.DataFrame, indicators: List[str]) -> pd.DataFrame:
        """Calculate advanced indicators using Pandas."""
        result_df = df.copy()
        
        if 'close_price' not in df.columns:
            return result_df
        
        try:
            # MACD (Moving Average Convergence Divergence)
            if 'macd' in indicators:
                ema_12 = result_df['close_price'].ewm(span=12).mean()
                ema_26 = result_df['close_price'].ewm(span=26).mean()
                result_df['macd'] = ema_12 - ema_26
                result_df['macd_signal'] = result_df['macd'].ewm(span=9).mean()
                result_df['macd_histogram'] = result_df['macd'] - result_df['macd_signal']
            
            # Average True Range (ATR)
            if 'atr' in indicators and all(col in df.columns for col in ['high_price', 'low_price']):
                high_low = result_df['high_price'] - result_df['low_price']
                high_close = (result_df['high_price'] - result_df['close_price'].shift(1)).abs()
                low_close = (result_df['low_price'] - result_df['close_price'].shift(1)).abs()
                
                result_df['true_range'] = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
                result_df['atr_14'] = result_df['true_range'].rolling(14).mean()
            
            # Williams %R
            if 'williams_r' in indicators and all(col in df.columns for col in ['high_price', 'low_price']):
                highest_high = result_df['high_price'].rolling(14).max()
                lowest_low = result_df['low_price'].rolling(14).min()
                result_df['williams_r_14'] = (highest_high - result_df['close_price']) / (highest_high - lowest_low) * -100
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error in Pandas advanced indicators: {e}")
            return result_df
    
    def calculate_portfolio_optimization_metrics(self, 
                                               portfolio_data: List[Dict],
                                               risk_free_rate: float = 0.02) -> Dict[str, Any]:
        """Calculate portfolio optimization metrics.
        
        Args:
            portfolio_data: Portfolio holdings data
            risk_free_rate: Risk-free rate for Sharpe ratio calculation
            
        Returns:
            Dictionary containing optimization metrics
        """
        try:
            if not portfolio_data:
                return {}
            
            # Calculate basic metrics first
            basic_metrics = self.calculate_portfolio_metrics(portfolio_data)
            
            # Add optimization-specific metrics
            optimization_metrics = {}
            
            # Calculate portfolio weights
            total_value = basic_metrics.get('total_value', 0)
            if total_value > 0:
                weights = []
                returns = []
                
                for holding in portfolio_data:
                    weight = holding.get('current_value', 0) / total_value
                    weights.append(weight)
                    
                    # Calculate individual return
                    current_val = holding.get('current_value', 0)
                    cost_basis = holding.get('cost_basis', 1)
                    if cost_basis > 0:
                        holding_return = (current_val - cost_basis) / cost_basis
                        returns.append(holding_return)
                
                if weights and returns:
                    # Portfolio-level calculations
                    avg_return = sum(r * w for r, w in zip(returns, weights))
                    
                    # Simple volatility estimate (would need historical data for proper calculation)
                    volatility = abs(sum((r - avg_return) ** 2 * w for r, w in zip(returns, weights))) ** 0.5
                    
                    # Sharpe ratio
                    sharpe_ratio = (avg_return - risk_free_rate) / volatility if volatility > 0 else 0
                    
                    optimization_metrics.update({
                        'portfolio_return': avg_return,
                        'portfolio_volatility': volatility,
                        'sharpe_ratio': sharpe_ratio,
                        'max_weight': max(weights) if weights else 0,
                        'min_weight': min(weights) if weights else 0,
                        'weight_concentration': max(weights) if weights else 0,
                    })
            
            # Combine with basic metrics
            return {**basic_metrics, **optimization_metrics}
            
        except Exception as e:
            logger.error(f"Error calculating portfolio optimization metrics: {e}")
            return self.calculate_portfolio_metrics(portfolio_data)
    
    def calculate_portfolio_metrics(self, 
                                  holdings_data: List[Dict]) -> Dict[str, Any]:
        """Calculate portfolio-level metrics using efficient DataFrame operations.
        
        Args:
            holdings_data: List of portfolio holding dictionaries
            
        Returns:
            Dictionary containing calculated portfolio metrics
        """
        if not holdings_data:
            return {
                'total_value': 0,
                'total_cost': 0,
                'total_return': 0,
                'return_percentage': 0,
                'holdings_count': 0,
            }
        
        df = self.create_price_dataframe(holdings_data)
        
        if self.polars_available and isinstance(df, pl.DataFrame):
            return self._calculate_portfolio_metrics_polars(df)
        elif self.pandas_available and isinstance(df, pd.DataFrame):
            return self._calculate_portfolio_metrics_pandas(df)
        else:
            raise ValueError(f"Unsupported DataFrame type: {type(df)}")
    
    def _calculate_portfolio_metrics_polars(self, df: pl.DataFrame) -> Dict[str, Any]:
        """Calculate portfolio metrics using Polars aggregations."""
        # Ensure required columns exist
        required_cols = ['current_value', 'cost_basis', 'quantity']
        for col in required_cols:
            if col not in df.columns:
                logger.warning(f"Required column '{col}' not found in holdings data")
                return {}
        
        # Calculate aggregated metrics using Polars
        metrics = df.select([
            pl.col('current_value').sum().alias('total_value'),
            pl.col('cost_basis').sum().alias('total_cost'),
            pl.len().alias('holdings_count'),
        ]).to_dicts()[0]
        
        # Calculate derived metrics
        total_return = metrics['total_value'] - metrics['total_cost']
        return_percentage = (
            (total_return / metrics['total_cost'] * 100) 
            if metrics['total_cost'] > 0 else 0
        )
        
        metrics.update({
            'total_return': total_return,
            'return_percentage': return_percentage,
        })
        
        return metrics
    
    def _calculate_portfolio_metrics_pandas(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate portfolio metrics using Pandas aggregations."""
        # Ensure required columns exist
        required_cols = ['current_value', 'cost_basis', 'quantity']
        for col in required_cols:
            if col not in df.columns:
                logger.warning(f"Required column '{col}' not found in holdings data")
                return {}
        
        # Calculate aggregated metrics
        total_value = df['current_value'].sum()
        total_cost = df['cost_basis'].sum()
        holdings_count = len(df)
        
        # Calculate derived metrics
        total_return = total_value - total_cost
        return_percentage = (
            (total_return / total_cost * 100) 
            if total_cost > 0 else 0
        )
        
        return {
            'total_value': total_value,
            'total_cost': total_cost,
            'total_return': total_return,
            'return_percentage': return_percentage,
            'holdings_count': holdings_count,
        }


# Global instance for easy access
polars_processor = PolarsDataProcessor()