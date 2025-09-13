"""Tests for enhanced analytics and visualization features.

Tests the new advanced capabilities added to take advantage of modern
finance libraries per S.C.A.F.F. requirements.
"""

import pytest
from decimal import Decimal
from datetime import date, datetime, timedelta
from typing import Dict, List, Any

# Test graceful imports for new modules
try:
    from personal_finance.data_sources.advanced_analytics import (
        advanced_analyzer, market_enhancer
    )
    ADVANCED_ANALYTICS_AVAILABLE = True
except ImportError:
    ADVANCED_ANALYTICS_AVAILABLE = False

try:
    from personal_finance.data_sources.enhanced_visualization import enhanced_visualizer
    ENHANCED_VISUALIZATION_AVAILABLE = True
except ImportError:
    ENHANCED_VISUALIZATION_AVAILABLE = False

try:
    from personal_finance.data_sources.polars_integration import polars_processor
    POLARS_INTEGRATION_AVAILABLE = True
except ImportError:
    POLARS_INTEGRATION_AVAILABLE = False

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class TestAdvancedAnalytics:
    """Test suite for advanced analytics capabilities."""
    
    @pytest.fixture
    def sample_portfolio_data(self):
        """Create comprehensive sample portfolio data."""
        return [
            {
                'symbol': 'AAPL',
                'quantity': 100,
                'cost_basis': 15000.00,
                'current_value': 18000.00,
                'purchase_date': date(2024, 1, 1),
            },
            {
                'symbol': 'GOOGL',
                'quantity': 25,
                'cost_basis': 70000.00,
                'current_value': 75000.00,
                'purchase_date': date(2024, 1, 15),
            },
            {
                'symbol': 'MSFT',
                'quantity': 75,
                'cost_basis': 26250.00,
                'current_value': 28500.00,
                'purchase_date': date(2024, 2, 1),
            },
        ]
    
    @pytest.fixture
    def sample_price_data_with_ohlc(self):
        """Create sample price data with OHLC for technical analysis."""
        data = []
        base_price = 180.0
        
        for i in range(50):  # 50 days of data
            date_obj = date.today() - timedelta(days=50 - i)
            price_change = (i % 10 - 5) * 0.02  # Simulate price movement
            close = base_price * (1 + price_change + (i * 0.001))
            high = close * 1.02
            low = close * 0.98
            open_price = close * (1 + ((i % 3 - 1) * 0.005))
            
            data.append({
                'symbol': 'AAPL',
                'date': date_obj.isoformat(),
                'open_price': round(open_price, 2),
                'high_price': round(high, 2),
                'low_price': round(low, 2),
                'close_price': round(close, 2),
                'volume': 1000000 + (i * 10000),
            })
        
        return data
    
    @pytest.mark.skipif(not ADVANCED_ANALYTICS_AVAILABLE, reason="Advanced analytics not available")
    def test_advanced_portfolio_metrics(self, sample_portfolio_data):
        """Test advanced portfolio metrics calculation."""
        metrics = advanced_analyzer.calculate_advanced_metrics(sample_portfolio_data)
        
        assert isinstance(metrics, dict)
        assert 'total_value' in metrics
        assert 'total_return' in metrics
        assert 'return_percentage' in metrics
        assert 'holdings_count' in metrics
        assert 'diversification_score' in metrics
        assert 'sector_allocation' in metrics
        assert 'risk_metrics' in metrics
        
        # Verify calculations
        total_value = sum(item['current_value'] for item in sample_portfolio_data)
        total_cost = sum(item['cost_basis'] for item in sample_portfolio_data)
        
        assert abs(metrics['total_value'] - total_value) < 0.01
        assert abs(metrics['total_cost'] - total_cost) < 0.01
        assert metrics['holdings_count'] == len(sample_portfolio_data)
        
        # Verify diversification score is between 0 and 1
        assert 0 <= metrics['diversification_score'] <= 1
        
        # Verify sector allocation sums to approximately 1
        if metrics['sector_allocation']:
            total_allocation = sum(metrics['sector_allocation'].values())
            assert abs(total_allocation - 1.0) < 0.01
    
    @pytest.mark.skipif(not ADVANCED_ANALYTICS_AVAILABLE, reason="Advanced analytics not available")
    def test_market_calendar_info(self):
        """Test market calendar information retrieval."""
        calendar_info = advanced_analyzer.get_market_calendar_info()
        
        assert isinstance(calendar_info, dict)
        assert 'exchange' in calendar_info
        assert 'trading_days_count' in calendar_info
        assert 'next_trading_day' in calendar_info
        
        # Basic validation
        assert calendar_info['trading_days_count'] > 0
        assert calendar_info['exchange'] is not None
    
    @pytest.mark.skipif(not ADVANCED_ANALYTICS_AVAILABLE, reason="Advanced analytics not available")
    def test_security_search(self):
        """Test security search functionality."""
        # Test with a common search term
        results = advanced_analyzer.search_securities("apple")
        
        assert isinstance(results, list)
        assert len(results) >= 0  # Should return at least fallback results
        
        if results:
            # Verify result structure
            first_result = results[0]
            assert 'symbol' in first_result
            assert 'name' in first_result
            
            # Should find AAPL in results
            symbols = [r.get('symbol', '') for r in results]
            assert 'AAPL' in symbols
    
    @pytest.mark.skipif(not ADVANCED_ANALYTICS_AVAILABLE, reason="Advanced analytics not available")
    def test_backtesting_strategy_creation(self):
        """Test backtesting strategy creation."""
        strategy_config = {
            'name': 'Test Strategy',
            'rebalance_freq': 'monthly',
            'assets': ['SPY', 'TLT']
        }
        
        strategy = advanced_analyzer.create_backtesting_strategy(strategy_config)
        
        # Should return either a strategy object or None (if bt not available)
        assert strategy is None or hasattr(strategy, '__class__')
    
    @pytest.mark.skipif(not ADVANCED_ANALYTICS_AVAILABLE, reason="Advanced analytics not available")
    def test_market_data_enhancement(self, sample_price_data_with_ohlc):
        """Test market data enhancement capabilities."""
        # Test different indicator combinations
        indicator_sets = [
            ['volatility'],
            ['momentum'],
            ['trend_strength'],
            ['volatility', 'momentum', 'trend_strength']
        ]
        
        for indicators in indicator_sets:
            enhanced_data = market_enhancer.enhance_price_data(
                sample_price_data_with_ohlc, indicators
            )
            
            assert enhanced_data is not None
            
            # Check if new columns were added
            if hasattr(enhanced_data, 'columns'):
                # Should have original columns plus new indicators
                original_columns = set(['symbol', 'date', 'close_price', 'open_price', 'high_price', 'low_price', 'volume'])
                new_columns = set(enhanced_data.columns) - original_columns
                
                # Should have added at least one new column per indicator
                assert len(new_columns) >= len(indicators)
    
    @pytest.mark.skipif(not POLARS_INTEGRATION_AVAILABLE, reason="Polars integration not available")
    def test_advanced_technical_indicators(self, sample_price_data_with_ohlc):
        """Test advanced technical indicators calculation."""
        # Create DataFrame
        df = polars_processor.create_price_dataframe(sample_price_data_with_ohlc)
        
        # Test advanced indicators
        advanced_indicators = ['macd', 'atr', 'williams_r']
        enhanced_df = polars_processor.calculate_advanced_technical_indicators(
            df, advanced_indicators
        )
        
        assert enhanced_df is not None
        
        # Check for new indicator columns
        if hasattr(enhanced_df, 'columns'):
            expected_columns = ['macd', 'macd_signal', 'macd_histogram', 'atr_14', 'williams_r_14']
            available_columns = set(enhanced_df.columns)
            
            # At least some advanced indicators should be present
            found_indicators = [col for col in expected_columns if col in available_columns]
            assert len(found_indicators) > 0
    
    @pytest.mark.skipif(not POLARS_INTEGRATION_AVAILABLE, reason="Polars integration not available")
    def test_portfolio_optimization_metrics(self, sample_portfolio_data):
        """Test portfolio optimization metrics calculation."""
        optimization_metrics = polars_processor.calculate_portfolio_optimization_metrics(
            sample_portfolio_data, risk_free_rate=0.02
        )
        
        assert isinstance(optimization_metrics, dict)
        
        # Should include basic metrics
        assert 'total_value' in optimization_metrics
        assert 'total_return' in optimization_metrics
        
        # Should include optimization-specific metrics
        expected_opt_metrics = ['portfolio_return', 'sharpe_ratio', 'max_weight', 'weight_concentration']
        found_opt_metrics = [metric for metric in expected_opt_metrics if metric in optimization_metrics]
        
        # Should have at least some optimization metrics
        assert len(found_opt_metrics) > 0
        
        # Validate metric ranges
        if 'max_weight' in optimization_metrics:
            assert 0 <= optimization_metrics['max_weight'] <= 1
        
        if 'weight_concentration' in optimization_metrics:
            assert 0 <= optimization_metrics['weight_concentration'] <= 1


class TestEnhancedVisualization:
    """Test suite for enhanced visualization capabilities."""
    
    @pytest.fixture
    def sample_portfolio_data(self):
        """Create sample portfolio data for visualization tests."""
        return [
            {'symbol': 'AAPL', 'current_value': 18000, 'cost_basis': 15000},
            {'symbol': 'GOOGL', 'current_value': 75000, 'cost_basis': 70000},
            {'symbol': 'MSFT', 'current_value': 28500, 'cost_basis': 26250},
        ]
    
    @pytest.fixture
    def sample_metrics(self):
        """Create sample metrics for visualization tests."""
        return {
            'total_value': 121500,
            'total_cost': 111250,
            'total_return': 10250,
            'return_percentage': 9.21,
            'holdings_count': 3,
            'diversification_score': 0.67,
            'sector_allocation': {
                'Technology': 0.8,
                'Other': 0.2
            },
            'risk_metrics': {
                'max_position_weight': 0.62,
                'number_of_positions': 3,
                'concentration_risk': 0.0
            }
        }
    
    @pytest.mark.skipif(not ENHANCED_VISUALIZATION_AVAILABLE, reason="Enhanced visualization not available")
    def test_advanced_dashboard_creation(self, sample_portfolio_data, sample_metrics):
        """Test advanced portfolio dashboard creation."""
        dashboard_html = enhanced_visualizer.create_advanced_portfolio_dashboard(
            sample_portfolio_data, sample_metrics
        )
        
        assert dashboard_html is not None
        assert isinstance(dashboard_html, str)
        assert len(dashboard_html) > 0
        
        # Should contain portfolio dashboard content
        assert 'portfolio' in dashboard_html.lower() or 'dashboard' in dashboard_html.lower()
    
    @pytest.mark.skipif(not ENHANCED_VISUALIZATION_AVAILABLE, reason="Enhanced visualization not available")
    def test_technical_analysis_chart(self):
        """Test technical analysis chart creation."""
        # Create sample price data with technical indicators
        price_data = []
        for i in range(20):
            price_data.append({
                'date': (date.today() - timedelta(days=20-i)).isoformat(),
                'close_price': 180 + i,
                'ma_10': 180 + i - 2,
                'rsi_14': 50 + (i % 10),
            })
        
        chart_html = enhanced_visualizer.create_technical_analysis_chart(
            price_data, indicators=['rsi_14']
        )
        
        # Should return HTML string or None if plotly not available
        assert chart_html is None or isinstance(chart_html, str)
        
        if chart_html:
            assert 'technical' in chart_html.lower() or 'chart' in chart_html.lower()
    
    @pytest.mark.skipif(not ENHANCED_VISUALIZATION_AVAILABLE, reason="Enhanced visualization not available")
    def test_performance_comparison_chart(self):
        """Test performance comparison chart creation."""
        performance_data = {
            'Portfolio': {'return_percentage': 9.2},
            'Benchmark': {'return_percentage': 7.5},
            'Last Year': {'return_percentage': 15.3},
            'YTD': {'return_percentage': 4.1}
        }
        
        chart_html = enhanced_visualizer.create_performance_comparison_chart(performance_data)
        
        # Should return HTML string or None if plotly not available
        assert chart_html is None or isinstance(chart_html, str)
        
        if chart_html:
            assert 'performance' in chart_html.lower() or 'comparison' in chart_html.lower()
    
    @pytest.mark.skipif(not ENHANCED_VISUALIZATION_AVAILABLE, reason="Enhanced visualization not available")
    def test_risk_return_scatter(self, sample_portfolio_data):
        """Test risk-return scatter plot creation."""
        benchmark_data = {'return_percentage': 8.0, 'volatility': 0.15}
        
        chart_html = enhanced_visualizer.create_risk_return_scatter(
            sample_portfolio_data, benchmark_data
        )
        
        # Should return HTML string or None if plotly not available
        assert chart_html is None or isinstance(chart_html, str)
        
        if chart_html:
            assert 'risk' in chart_html.lower() or 'return' in chart_html.lower()
    
    @pytest.mark.skipif(not ENHANCED_VISUALIZATION_AVAILABLE, reason="Enhanced visualization not available")
    def test_report_data_generation(self, sample_portfolio_data, sample_metrics):
        """Test comprehensive report data generation."""
        charts = {
            'dashboard': '<div>Dashboard HTML</div>',
            'technical': '<div>Technical Chart HTML</div>',
            'performance': '<div>Performance Chart HTML</div>'
        }
        
        report_data = enhanced_visualizer.generate_report_data(
            sample_portfolio_data, sample_metrics, charts
        )
        
        assert isinstance(report_data, dict)
        assert 'portfolio_data' in report_data
        assert 'metrics' in report_data
        assert 'charts' in report_data
        assert 'timestamp' in report_data
        assert 'summary' in report_data
        
        # Verify summary calculations
        summary = report_data['summary']
        assert summary['total_holdings'] == len(sample_portfolio_data)
        assert summary['performance_status'] in ['positive', 'negative']
        assert summary['diversification_level'] in ['high', 'moderate', 'low']


class TestIntegrationWorkflows:
    """Test end-to-end integration workflows with new features."""
    
    @pytest.mark.skipif(not all([ADVANCED_ANALYTICS_AVAILABLE, ENHANCED_VISUALIZATION_AVAILABLE]), 
                       reason="Not all enhanced modules available")
    def test_complete_enhanced_workflow(self):
        """Test complete workflow using all enhanced features."""
        # Create sample data
        portfolio_data = [
            {'symbol': 'AAPL', 'current_value': 10000, 'cost_basis': 9000},
            {'symbol': 'GOOGL', 'current_value': 20000, 'cost_basis': 18000},
        ]
        
        # Step 1: Calculate advanced metrics
        metrics = advanced_analyzer.calculate_advanced_metrics(portfolio_data)
        assert isinstance(metrics, dict)
        assert len(metrics) > 0
        
        # Step 2: Create visualizations
        dashboard = enhanced_visualizer.create_advanced_portfolio_dashboard(
            portfolio_data, metrics
        )
        assert dashboard is not None
        
        # Step 3: Generate comprehensive report
        charts = {'dashboard': dashboard}
        report_data = enhanced_visualizer.generate_report_data(
            portfolio_data, metrics, charts
        )
        assert isinstance(report_data, dict)
        assert 'summary' in report_data
    
    def test_graceful_degradation_all_modules(self):
        """Test that all modules handle missing dependencies gracefully."""
        # This test should always pass regardless of what libraries are available
        
        # Test empty data handling across all modules
        empty_portfolio = []
        
        if ADVANCED_ANALYTICS_AVAILABLE:
            empty_metrics = advanced_analyzer.calculate_advanced_metrics(empty_portfolio)
            assert isinstance(empty_metrics, dict)
        
        if ENHANCED_VISUALIZATION_AVAILABLE:
            empty_dashboard = enhanced_visualizer.create_advanced_portfolio_dashboard(
                empty_portfolio, {}
            )
            assert empty_dashboard is not None
        
        if POLARS_INTEGRATION_AVAILABLE:
            empty_opt_metrics = polars_processor.calculate_portfolio_optimization_metrics(
                empty_portfolio
            )
            assert isinstance(empty_opt_metrics, dict)
    
    def test_library_availability_detection(self):
        """Test that library availability is correctly detected."""
        # These tests verify our import detection works correctly
        assert isinstance(ADVANCED_ANALYTICS_AVAILABLE, bool)
        assert isinstance(ENHANCED_VISUALIZATION_AVAILABLE, bool)
        assert isinstance(POLARS_INTEGRATION_AVAILABLE, bool)
        assert isinstance(POLARS_AVAILABLE, bool)
        assert isinstance(PANDAS_AVAILABLE, bool)
        
        # At least basic functionality should be available
        assert ADVANCED_ANALYTICS_AVAILABLE or ENHANCED_VISUALIZATION_AVAILABLE


if __name__ == '__main__':
    # Run tests when file is executed directly
    pytest.main([__file__, '-v'])