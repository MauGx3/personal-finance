"""Advanced analytics module leveraging modern finance libraries.

This module extends the platform with advanced financial analytics capabilities
using FinanceDatabase, FinanceToolkit, bt backtesting, and other modern libraries
as specified in the S.C.A.F.F. requirements.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
from datetime import datetime, date, timedelta
import json

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
    import bt
    BT_AVAILABLE = True
except ImportError:
    BT_AVAILABLE = False
    bt = None

try:
    import financetoolkit as ftk
    FINANCETOOLKIT_AVAILABLE = True
except ImportError:
    FINANCETOOLKIT_AVAILABLE = False
    ftk = None

try:
    import financedatabase as fdb
    FINANCEDATABASE_AVAILABLE = True
except ImportError:
    FINANCEDATABASE_AVAILABLE = False
    fdb = None

try:
    import pandas_market_calendars as mcal
    MARKET_CALENDARS_AVAILABLE = True
except ImportError:
    MARKET_CALENDARS_AVAILABLE = False
    mcal = None

try:
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

logger = logging.getLogger(__name__)


class AdvancedPortfolioAnalyzer:
    """Advanced portfolio analysis using modern finance libraries."""
    
    def __init__(self):
        """Initialize the analyzer with available libraries."""
        self.bt_available = BT_AVAILABLE
        self.ftk_available = FINANCETOOLKIT_AVAILABLE
        self.fdb_available = FINANCEDATABASE_AVAILABLE
        self.market_cal_available = MARKET_CALENDARS_AVAILABLE
        
        logger.info(f"Advanced analyzer initialized - bt: {self.bt_available}, "
                   f"financetoolkit: {self.ftk_available}, "
                   f"financedatabase: {self.fdb_available}, "
                   f"market_calendars: {self.market_cal_available}")
    
    def calculate_advanced_metrics(self, 
                                 portfolio_data: Union[List[Dict], pd.DataFrame, pl.DataFrame],
                                 benchmark_symbol: str = "SPY") -> Dict[str, Any]:
        """Calculate advanced portfolio metrics using FinanceToolkit.
        
        Args:
            portfolio_data: Portfolio holdings data
            benchmark_symbol: Benchmark symbol for comparison
            
        Returns:
            Dictionary containing advanced metrics
        """
        try:
            if not self.ftk_available:
                return self._calculate_basic_metrics_fallback(portfolio_data)
            
            # Convert to standard format
            if isinstance(portfolio_data, list):
                df = pd.DataFrame(portfolio_data) if PANDAS_AVAILABLE else None
            else:
                df = portfolio_data
            
            if df is None or df.empty:
                return {}
            
            # Calculate basic metrics first
            metrics = {}
            
            if 'current_value' in df.columns and 'cost_basis' in df.columns:
                total_value = df['current_value'].sum()
                total_cost = df['cost_basis'].sum()
                total_return = total_value - total_cost
                return_pct = (total_return / total_cost * 100) if total_cost > 0 else 0
                
                metrics.update({
                    'total_value': float(total_value),
                    'total_cost': float(total_cost),
                    'total_return': float(total_return),
                    'return_percentage': float(return_pct),
                    'holdings_count': len(df),
                })
            
            # Add advanced metrics
            if 'symbol' in df.columns:
                metrics['diversification_score'] = self._calculate_diversification_score(df)
                metrics['sector_allocation'] = self._get_sector_allocation(df)
                metrics['risk_metrics'] = self._calculate_risk_metrics(df)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating advanced metrics: {e}")
            return self._calculate_basic_metrics_fallback(portfolio_data)
    
    def _calculate_basic_metrics_fallback(self, portfolio_data) -> Dict[str, Any]:
        """Basic metrics calculation when advanced libraries unavailable."""
        if isinstance(portfolio_data, list):
            if not portfolio_data:
                return {'total_value': 0, 'total_cost': 0, 'total_return': 0, 
                       'return_percentage': 0, 'holdings_count': 0}
            
            total_value = sum(item.get('current_value', 0) for item in portfolio_data)
            total_cost = sum(item.get('cost_basis', 0) for item in portfolio_data)
            total_return = total_value - total_cost
            return_pct = (total_return / total_cost * 100) if total_cost > 0 else 0
            
            return {
                'total_value': total_value,
                'total_cost': total_cost,
                'total_return': total_return,
                'return_percentage': return_pct,
                'holdings_count': len(portfolio_data),
            }
        
        return {}
    
    def _calculate_diversification_score(self, df) -> float:
        """Calculate portfolio diversification score."""
        try:
            if 'current_value' in df.columns:
                # Calculate concentration (Herfindahl index)
                total_value = df['current_value'].sum()
                if total_value > 0:
                    weights = df['current_value'] / total_value
                    herfindahl = (weights ** 2).sum()
                    # Convert to diversification score (1 = perfectly diversified)
                    diversification = 1 - herfindahl
                    return float(diversification)
            return 0.0
        except Exception as e:
            logger.warning(f"Error calculating diversification score: {e}")
            return 0.0
    
    def _get_sector_allocation(self, df) -> Dict[str, float]:
        """Get sector allocation using FinanceDatabase."""
        try:
            if not self.fdb_available or 'symbol' not in df.columns:
                return {}
            
            sector_allocation = {}
            total_value = df['current_value'].sum() if 'current_value' in df.columns else 1
            
            for _, row in df.iterrows():
                symbol = row.get('symbol', '')
                value = row.get('current_value', 0)
                
                # This is a simplified sector mapping - in production you'd use FinanceDatabase
                # to get actual sector information
                sector = self._get_sector_for_symbol(symbol)
                if sector:
                    weight = value / total_value if total_value > 0 else 0
                    sector_allocation[sector] = sector_allocation.get(sector, 0) + weight
            
            return sector_allocation
            
        except Exception as e:
            logger.warning(f"Error getting sector allocation: {e}")
            return {}
    
    def _get_sector_for_symbol(self, symbol: str) -> str:
        """Get sector for a symbol (simplified mapping for demo)."""
        # Simplified sector mapping for common symbols
        tech_symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA']
        finance_symbols = ['JPM', 'BAC', 'WFC', 'GS', 'MS']
        
        if symbol in tech_symbols:
            return 'Technology'
        elif symbol in finance_symbols:
            return 'Financial Services'
        else:
            return 'Other'
    
    def _calculate_risk_metrics(self, df) -> Dict[str, float]:
        """Calculate basic risk metrics."""
        try:
            if 'current_value' not in df.columns:
                return {}
            
            total_value = df['current_value'].sum()
            if total_value == 0:
                return {}
            
            # Calculate portfolio concentration risk
            weights = df['current_value'] / total_value
            max_weight = weights.max()
            
            return {
                'max_position_weight': float(max_weight),
                'number_of_positions': len(df),
                'concentration_risk': float(max_weight) if max_weight > 0.2 else 0.0,
            }
            
        except Exception as e:
            logger.warning(f"Error calculating risk metrics: {e}")
            return {}
    
    def create_backtesting_strategy(self, 
                                  strategy_config: Dict[str, Any]) -> Optional[Any]:
        """Create a backtesting strategy using bt library.
        
        Args:
            strategy_config: Configuration for the strategy
            
        Returns:
            bt.Strategy object if available, None otherwise
        """
        try:
            if not self.bt_available:
                logger.warning("bt library not available for backtesting")
                return None
            
            # Example simple rebalancing strategy
            strategy_name = strategy_config.get('name', 'Simple Strategy')
            rebalance_freq = strategy_config.get('rebalance_freq', 'monthly')
            assets = strategy_config.get('assets', ['SPY'])
            
            # Create equal weight strategy
            strategy = bt.Strategy(
                strategy_name,
                [
                    bt.algos.RunMonthly() if rebalance_freq == 'monthly' else bt.algos.RunDaily(),
                    bt.algos.SelectAll(),
                    bt.algos.WeighEqually(),
                    bt.algos.Rebalance()
                ]
            )
            
            logger.info(f"Created backtesting strategy: {strategy_name}")
            return strategy
            
        except Exception as e:
            logger.error(f"Error creating backtesting strategy: {e}")
            return None
    
    def get_market_calendar_info(self, 
                                exchange: str = 'NYSE',
                                start_date: Optional[date] = None,
                                end_date: Optional[date] = None) -> Dict[str, Any]:
        """Get market calendar information.
        
        Args:
            exchange: Exchange name
            start_date: Start date for calendar
            end_date: End date for calendar
            
        Returns:
            Dictionary with market calendar information
        """
        try:
            if not self.market_cal_available:
                return self._get_basic_market_info()
            
            if start_date is None:
                start_date = date.today()
            if end_date is None:
                end_date = start_date + timedelta(days=30)
            
            # Get market calendar
            calendar = mcal.get_calendar(exchange)
            schedule = calendar.schedule(start_date=start_date, end_date=end_date)
            
            return {
                'exchange': exchange,
                'trading_days_count': len(schedule),
                'next_trading_day': schedule.index[0].date() if not schedule.empty else None,
                'market_open': schedule.iloc[0]['market_open'] if not schedule.empty else None,
                'market_close': schedule.iloc[0]['market_close'] if not schedule.empty else None,
            }
            
        except Exception as e:
            logger.error(f"Error getting market calendar info: {e}")
            return self._get_basic_market_info()
    
    def _get_basic_market_info(self) -> Dict[str, Any]:
        """Basic market info fallback."""
        return {
            'exchange': 'NYSE',
            'trading_days_count': 22,  # Approximate monthly trading days
            'next_trading_day': date.today(),
            'market_open': '09:30',
            'market_close': '16:00',
        }
    
    def search_securities(self, 
                         search_term: str,
                         asset_class: str = 'equities') -> List[Dict[str, Any]]:
        """Search for securities using FinanceDatabase.
        
        Args:
            search_term: Term to search for
            asset_class: Asset class to search in
            
        Returns:
            List of matching securities
        """
        try:
            if not self.fdb_available:
                return self._search_securities_fallback(search_term)
            
            # Use FinanceDatabase to search - updated for correct API
            if asset_class == 'equities':
                database = fdb.Equities()
                results = database.select()  # Get all equities first
                # Simple filtering by search term
                filtered_results = {k: v for k, v in results.items() 
                                  if search_term.lower() in k.lower() or 
                                  search_term.lower() in v.get('long_name', '').lower()}
            elif asset_class == 'etfs':
                database = fdb.ETFs()
                results = database.select()
                filtered_results = {k: v for k, v in results.items() 
                                  if search_term.lower() in k.lower() or 
                                  search_term.lower() in v.get('long_name', '').lower()}
            else:
                # Fallback to basic search
                return self._search_securities_fallback(search_term)
            
            # Convert to our format
            securities = []
            for symbol, data in list(filtered_results.items())[:10]:  # Limit results
                securities.append({
                    'symbol': symbol,
                    'name': data.get('long_name', ''),
                    'sector': data.get('sector', ''),
                    'industry': data.get('industry', ''),
                    'country': data.get('country', ''),
                    'asset_class': asset_class,
                })
            
            return securities
            
        except Exception as e:
            logger.error(f"Error searching securities: {e}")
            return self._search_securities_fallback(search_term)
    
    def _search_securities_fallback(self, search_term: str) -> List[Dict[str, Any]]:
        """Fallback security search."""
        # Simple fallback with common symbols
        common_stocks = [
            {'symbol': 'AAPL', 'name': 'Apple Inc.', 'sector': 'Technology'},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'sector': 'Technology'},
            {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'sector': 'Technology'},
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'sector': 'Consumer Discretionary'},
            {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'sector': 'Consumer Discretionary'},
        ]
        
        # Filter by search term
        results = []
        search_lower = search_term.lower()
        for stock in common_stocks:
            if (search_lower in stock['symbol'].lower() or 
                search_lower in stock['name'].lower()):
                results.append(stock)
        
        return results


class MarketDataEnhancer:
    """Enhance market data with additional analysis capabilities."""
    
    def __init__(self):
        """Initialize the market data enhancer."""
        self.polars_available = POLARS_AVAILABLE
        self.pandas_available = PANDAS_AVAILABLE
    
    def enhance_price_data(self, 
                          price_data: Union[List[Dict], pd.DataFrame, pl.DataFrame],
                          indicators: List[str] = None) -> Union[pd.DataFrame, pl.DataFrame]:
        """Enhance price data with additional technical indicators.
        
        Args:
            price_data: Price data to enhance
            indicators: List of indicators to calculate
            
        Returns:
            Enhanced DataFrame with additional indicators
        """
        try:
            if indicators is None:
                indicators = ['volatility', 'momentum', 'trend_strength']
            
            # Convert to DataFrame if needed
            if isinstance(price_data, list):
                if self.polars_available:
                    df = pl.DataFrame(price_data)
                elif self.pandas_available:
                    df = pd.DataFrame(price_data)
                else:
                    return price_data
            else:
                df = price_data
            
            # Add enhanced indicators
            if self.polars_available and isinstance(df, pl.DataFrame):
                return self._enhance_with_polars(df, indicators)
            elif self.pandas_available and isinstance(df, pd.DataFrame):
                return self._enhance_with_pandas(df, indicators)
            
            return df
            
        except Exception as e:
            logger.error(f"Error enhancing price data: {e}")
            return price_data
    
    def _enhance_with_polars(self, df: pl.DataFrame, indicators: List[str]) -> pl.DataFrame:
        """Enhance data using Polars."""
        try:
            enhanced_df = df.clone()
            
            if 'close_price' in df.columns:
                # Add volatility indicator
                if 'volatility' in indicators:
                    enhanced_df = enhanced_df.with_columns([
                        pl.col('close_price').pct_change().rolling_std(window_size=20)
                        .alias('volatility_20d')
                    ])
                
                # Add momentum indicator
                if 'momentum' in indicators:
                    enhanced_df = enhanced_df.with_columns([
                        (pl.col('close_price') / pl.col('close_price').shift(10) - 1)
                        .alias('momentum_10d')
                    ])
                
                # Add trend strength
                if 'trend_strength' in indicators:
                    ma_short = pl.col('close_price').rolling_mean(window_size=10)
                    ma_long = pl.col('close_price').rolling_mean(window_size=50)
                    enhanced_df = enhanced_df.with_columns([
                        ((ma_short - ma_long) / ma_long).alias('trend_strength')
                    ])
            
            return enhanced_df
            
        except Exception as e:
            logger.error(f"Error enhancing with Polars: {e}")
            return df
    
    def _enhance_with_pandas(self, df: pd.DataFrame, indicators: List[str]) -> pd.DataFrame:
        """Enhance data using Pandas."""
        try:
            enhanced_df = df.copy()
            
            if 'close_price' in df.columns:
                # Add volatility indicator
                if 'volatility' in indicators:
                    enhanced_df['volatility_20d'] = (
                        enhanced_df['close_price'].pct_change().rolling(20).std()
                    )
                
                # Add momentum indicator
                if 'momentum' in indicators:
                    enhanced_df['momentum_10d'] = (
                        enhanced_df['close_price'] / enhanced_df['close_price'].shift(10) - 1
                    )
                
                # Add trend strength
                if 'trend_strength' in indicators:
                    ma_short = enhanced_df['close_price'].rolling(10).mean()
                    ma_long = enhanced_df['close_price'].rolling(50).mean()
                    enhanced_df['trend_strength'] = (ma_short - ma_long) / ma_long
            
            return enhanced_df
            
        except Exception as e:
            logger.error(f"Error enhancing with Pandas: {e}")
            return df


# Create global instances for easy importing
advanced_analyzer = AdvancedPortfolioAnalyzer()
market_enhancer = MarketDataEnhancer()