"""Comprehensive integration tests for enhanced data analysis capabilities.

Tests the integration of modern data analysis libraries (Polars, DataProfiler,
pyjanitor) with the existing Django personal finance platform.
"""

import pytest
import logging
from decimal import Decimal
from datetime import date, datetime, timedelta
from typing import Dict, List, Any

# Test graceful imports
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

try:
    from personal_finance.data_sources.polars_integration import polars_processor
    POLARS_INTEGRATION_AVAILABLE = True
except ImportError:
    POLARS_INTEGRATION_AVAILABLE = False

try:
    from personal_finance.data_sources.data_profiling import financial_profiler
    DATA_PROFILING_AVAILABLE = True
except ImportError:
    DATA_PROFILING_AVAILABLE = False

try:
    from personal_finance.data_sources.data_cleaning import financial_cleaner
    DATA_CLEANING_AVAILABLE = True
except ImportError:
    DATA_CLEANING_AVAILABLE = False

logger = logging.getLogger(__name__)


class TestDataAnalysisIntegration:
    """Test suite for enhanced data analysis integration."""
    
    @pytest.fixture
    def sample_price_data(self):
        """Create sample price data for testing."""
        return [
            {
                'symbol': 'AAPL',
                'date': '2024-01-01',
                'open_price': 180.0,
                'high_price': 185.0,
                'low_price': 178.0,
                'close_price': 182.0,
                'volume': 1000000,
                'adjusted_close': 182.0,
            },
            {
                'symbol': 'AAPL',
                'date': '2024-01-02',
                'open_price': 182.0,
                'high_price': 188.0,
                'low_price': 181.0,
                'close_price': 186.0,
                'volume': 1200000,
                'adjusted_close': 186.0,
            },
            {
                'symbol': 'AAPL',
                'date': '2024-01-03',
                'open_price': 186.0,
                'high_price': 190.0,
                'low_price': 184.0,
                'close_price': 189.0,
                'volume': 950000,
                'adjusted_close': 189.0,
            },
        ]
    
    @pytest.fixture
    def sample_portfolio_data(self):
        """Create sample portfolio data for testing."""
        return [
            {
                'symbol': 'AAPL',
                'quantity': 50,
                'cost_basis': 9000.00,
                'current_value': 9500.00,
                'purchase_date': date(2024, 1, 1),
            },
            {
                'symbol': 'GOOGL',
                'quantity': 25,
                'cost_basis': 7500.00,
                'current_value': 8000.00,
                'purchase_date': date(2024, 1, 15),
            },
            {
                'symbol': 'MSFT',
                'quantity': 30,
                'cost_basis': 10500.00,
                'current_value': 11200.00,
                'purchase_date': date(2024, 2, 1),
            },
        ]
    
    @pytest.fixture
    def messy_financial_data(self):
        """Create messy financial data for cleaning tests."""
        return [
            {
                'Stock Symbol': 'AAPL',
                'Purchase Price': '$150.50',
                'Current Price': '$180,25',
                'Quantity Owned': '100',
                'Purchase Date': '2024-01-01',
                'Total Value': '($18,025.00)',  # Negative in parentheses
            },
            {
                'Stock Symbol': 'GOOGL',
                'Purchase Price': '€2,800.75',
                'Current Price': '3200.00',
                'Quantity Owned': '25',
                'Purchase Date': '2024/01/15',
                'Total Value': '80000.00',
            },
        ]
    
    @pytest.mark.skipif(not POLARS_INTEGRATION_AVAILABLE, reason="Polars integration not available")
    def test_polars_integration_basic_functionality(self, sample_price_data):
        """Test basic Polars integration functionality."""
        # Test DataFrame creation
        df = polars_processor.create_price_dataframe(sample_price_data)
        assert df is not None
        
        if POLARS_AVAILABLE:
            assert isinstance(df, pl.DataFrame)
            assert df.height == len(sample_price_data)
        elif PANDAS_AVAILABLE:
            assert isinstance(df, pd.DataFrame)
            assert len(df) == len(sample_price_data)
    
    @pytest.mark.skipif(not POLARS_INTEGRATION_AVAILABLE, reason="Polars integration not available")
    def test_moving_averages_calculation(self, sample_price_data):
        """Test moving averages calculation."""
        df = polars_processor.create_price_dataframe(sample_price_data)
        df_with_ma = polars_processor.calculate_moving_averages(df, windows=[2])
        
        assert df_with_ma is not None
        
        # Check that moving average column was added
        if POLARS_AVAILABLE and isinstance(df_with_ma, pl.DataFrame):
            assert 'ma_2' in df_with_ma.columns
        elif PANDAS_AVAILABLE and isinstance(df_with_ma, pd.DataFrame):
            assert 'ma_2' in df_with_ma.columns
    
    @pytest.mark.skipif(not POLARS_INTEGRATION_AVAILABLE, reason="Polars integration not available")
    def test_technical_indicators_calculation(self, sample_price_data):
        """Test technical indicators calculation."""
        # Need more data points for meaningful technical indicators
        extended_data = sample_price_data * 20  # Repeat data to have enough points
        for i, item in enumerate(extended_data):
            item['date'] = (datetime(2024, 1, 1) + timedelta(days=i)).strftime('%Y-%m-%d')
            item['close_price'] = 180 + (i * 0.5)  # Trending upward
        
        df = polars_processor.create_price_dataframe(extended_data)
        df_with_indicators = polars_processor.calculate_technical_indicators(df)
        
        assert df_with_indicators is not None
        
        # Check that technical indicator columns were added
        if POLARS_AVAILABLE and isinstance(df_with_indicators, pl.DataFrame):
            expected_columns = ['rsi_14', 'bb_upper', 'bb_lower', 'bb_middle']
            for col in expected_columns:
                assert col in df_with_indicators.columns
        elif PANDAS_AVAILABLE and isinstance(df_with_indicators, pd.DataFrame):
            expected_columns = ['rsi_14', 'bb_upper', 'bb_lower', 'bb_middle']
            for col in expected_columns:
                assert col in df_with_indicators.columns
    
    @pytest.mark.skipif(not POLARS_INTEGRATION_AVAILABLE, reason="Polars integration not available")
    def test_portfolio_metrics_calculation(self, sample_portfolio_data):
        """Test portfolio metrics calculation."""
        metrics = polars_processor.calculate_portfolio_metrics(sample_portfolio_data)
        
        assert isinstance(metrics, dict)
        assert 'total_value' in metrics
        assert 'total_cost' in metrics
        assert 'total_return' in metrics
        assert 'return_percentage' in metrics
        assert 'holdings_count' in metrics
        
        # Verify calculations
        expected_total_value = sum(item['current_value'] for item in sample_portfolio_data)
        expected_total_cost = sum(item['cost_basis'] for item in sample_portfolio_data)
        
        assert abs(metrics['total_value'] - expected_total_value) < 0.01
        assert abs(metrics['total_cost'] - expected_total_cost) < 0.01
        assert metrics['holdings_count'] == len(sample_portfolio_data)
    
    @pytest.mark.skipif(not DATA_PROFILING_AVAILABLE, reason="Data profiling not available")
    def test_data_profiling_basic_functionality(self, sample_portfolio_data):
        """Test basic data profiling functionality."""
        if PANDAS_AVAILABLE:
            df = pd.DataFrame(sample_portfolio_data)
            profile_results = financial_profiler.profile_financial_data(df, 'dataframe')
            
            assert isinstance(profile_results, dict)
            assert 'timestamp' in profile_results
            assert 'column_profiles' in profile_results
            assert 'sensitive_data_alerts' in profile_results
            assert 'recommendations' in profile_results
    
    @pytest.mark.skipif(not DATA_PROFILING_AVAILABLE, reason="Data profiling not available")
    def test_portfolio_data_profiling(self, sample_portfolio_data):
        """Test specialized portfolio data profiling."""
        profile_results = financial_profiler.profile_portfolio_data(sample_portfolio_data)
        
        assert isinstance(profile_results, dict)
        # Should have some profiling information even in fallback mode
        assert len(profile_results) > 0
    
    @pytest.mark.skipif(not DATA_PROFILING_AVAILABLE, reason="Data profiling not available")
    def test_financial_data_type_validation(self):
        """Test financial data type validation."""
        test_data = {
            'price': 150.50,  # float - should trigger warning
            'amount': Decimal('1000.00'),  # Decimal - good
            'quantity': 100,  # int - good
            'name': 'Apple Inc.',  # string - ignored
        }
        
        validation_results = financial_profiler.validate_financial_data_types(test_data)
        
        assert isinstance(validation_results, dict)
        assert 'valid' in validation_results
        assert 'issues' in validation_results
        
        # Should flag the float price
        assert len(validation_results['issues']) > 0
        assert validation_results['issues'][0]['field'] == 'price'
        assert validation_results['issues'][0]['issue'] == 'float_precision'
    
    @pytest.mark.skipif(not DATA_CLEANING_AVAILABLE, reason="Data cleaning not available")
    def test_data_cleaning_basic_functionality(self, messy_financial_data):
        """Test basic data cleaning functionality."""
        cleaned_data = financial_cleaner.clean_portfolio_data(messy_financial_data)
        
        assert isinstance(cleaned_data, list)
        assert len(cleaned_data) == len(messy_financial_data)
        
        # Check that data was cleaned
        for item in cleaned_data:
            assert isinstance(item, dict)
            # Column names should be standardized
            assert any('_' in key for key in item.keys())  # Should have snake_case keys
    
    @pytest.mark.skipif(not (DATA_CLEANING_AVAILABLE and PANDAS_AVAILABLE), reason="Data cleaning or pandas not available")
    def test_dataframe_cleaning_pandas(self, messy_financial_data):
        """Test DataFrame cleaning with Pandas."""
        # Create messy DataFrame
        df = pd.DataFrame(messy_financial_data)
        
        # Clean the DataFrame
        cleaned_df = financial_cleaner.clean_financial_dataframe(df)
        
        assert isinstance(cleaned_df, pd.DataFrame)
        assert len(cleaned_df) == len(df)
        
        # Check column name standardization
        for col in cleaned_df.columns:
            assert col.islower()  # Should be lowercase
            assert ' ' not in col  # Should not have spaces
    
    @pytest.mark.skipif(not (DATA_CLEANING_AVAILABLE and POLARS_AVAILABLE), reason="Data cleaning or polars not available")
    def test_dataframe_cleaning_polars(self, messy_financial_data):
        """Test DataFrame cleaning with Polars."""
        # Create messy DataFrame
        df = pl.DataFrame(messy_financial_data)
        
        # Clean the DataFrame
        cleaned_df = financial_cleaner.clean_financial_dataframe(df)
        
        assert isinstance(cleaned_df, pl.DataFrame)
        assert cleaned_df.height == df.height
        
        # Check column name standardization
        for col in cleaned_df.columns:
            assert col.islower()  # Should be lowercase
            assert ' ' not in col  # Should not have spaces
    
    @pytest.mark.skipif(not DATA_CLEANING_AVAILABLE, reason="Data cleaning not available")
    def test_financial_value_cleaning(self):
        """Test financial value cleaning functionality."""
        test_values = [
            '$1,234.56',
            '€2,500.00',
            '(1,000.00)',  # Negative in parentheses
            '£500',
            '1234.567',  # High precision
            None,
            '',
        ]
        
        cleaned_values = []
        for value in test_values:
            cleaned = financial_cleaner.clean_financial_value(value)
            cleaned_values.append(cleaned)
        
        # Check that values were properly cleaned
        assert cleaned_values[0] == Decimal('1234.56')  # Dollar sign removed
        assert cleaned_values[1] == Decimal('2500.00')  # Euro sign and comma removed
        assert cleaned_values[2] == Decimal('-1000.00')  # Parentheses converted to negative
        assert cleaned_values[3] == Decimal('500')  # Pound sign removed
        assert cleaned_values[4] == Decimal('1234.567')  # High precision preserved
        assert cleaned_values[5] is None  # None handled
        assert cleaned_values[6] is None  # Empty string handled
    
    @pytest.mark.skipif(not (DATA_CLEANING_AVAILABLE and PANDAS_AVAILABLE), reason="Requirements not available")
    def test_cleaning_report_generation(self, messy_financial_data):
        """Test cleaning report generation."""
        # Create and clean DataFrame
        original_df = pd.DataFrame(messy_financial_data)
        cleaned_df = financial_cleaner.clean_financial_dataframe(original_df)
        
        # Generate report
        report = financial_cleaner.generate_cleaning_report(original_df, cleaned_df)
        
        assert isinstance(report, dict)
        assert 'timestamp' in report
        assert 'cleaning_summary' in report
        assert 'changes_made' in report
        assert 'recommendations' in report
    
    def test_library_availability_checks(self):
        """Test that library availability is properly detected."""
        # These tests should always pass as they test the import detection
        assert isinstance(POLARS_AVAILABLE, bool)
        assert isinstance(PANDAS_AVAILABLE, bool)
        assert isinstance(POLARS_INTEGRATION_AVAILABLE, bool)
        assert isinstance(DATA_PROFILING_AVAILABLE, bool)
        assert isinstance(DATA_CLEANING_AVAILABLE, bool)
        
        # At least one DataFrame library should be available in CI
        if not (POLARS_AVAILABLE or PANDAS_AVAILABLE):
            pytest.skip("No DataFrame libraries available for testing")
    
    def test_graceful_degradation(self):
        """Test that modules gracefully handle missing dependencies."""
        # This test ensures that missing optional dependencies don't break the code
        
        # Test empty data handling
        if POLARS_INTEGRATION_AVAILABLE:
            empty_metrics = polars_processor.calculate_portfolio_metrics([])
            assert isinstance(empty_metrics, dict)
            assert empty_metrics['total_value'] == 0
        
        if DATA_CLEANING_AVAILABLE:
            empty_cleaned = financial_cleaner.clean_portfolio_data([])
            assert isinstance(empty_cleaned, list)
            assert len(empty_cleaned) == 0
        
        if DATA_PROFILING_AVAILABLE:
            empty_profile = financial_profiler.profile_portfolio_data([])
            assert isinstance(empty_profile, dict)


@pytest.mark.integration
class TestEndToEndDataAnalysisWorkflow:
    """End-to-end tests for complete data analysis workflows."""
    
    @pytest.mark.skipif(not all([POLARS_INTEGRATION_AVAILABLE, DATA_CLEANING_AVAILABLE, DATA_PROFILING_AVAILABLE]), 
                       reason="Not all data analysis modules available")
    def test_complete_analysis_workflow(self):
        """Test a complete data analysis workflow using all modules."""
        # Sample raw data with common issues
        raw_data = [
            {
                'Stock Symbol': 'AAPL',
                'Purchase Price': '$150.50',
                'Current Price': '$180.25',
                'Shares': '100',
                'Buy Date': '2024-01-01',
            },
            {
                'Stock Symbol': 'GOOGL',
                'Purchase Price': '€2,800.75',
                'Current Price': '3200.00',
                'Shares': '25',
                'Buy Date': '2024/01/15',
            },
        ]
        
        # Step 1: Clean the data
        cleaned_data = financial_cleaner.clean_portfolio_data(raw_data)
        assert len(cleaned_data) == len(raw_data)
        
        # Step 2: Profile the data (if available)
        if DATA_PROFILING_AVAILABLE and PANDAS_AVAILABLE:
            profile_results = financial_profiler.profile_portfolio_data(cleaned_data)
            assert isinstance(profile_results, dict)
        
        # Step 3: Enhanced analysis (if available)
        if POLARS_INTEGRATION_AVAILABLE:
            # Transform for portfolio metrics calculation
            portfolio_data = []
            for item in cleaned_data:
                portfolio_item = {
                    'symbol': item.get('stock_symbol', ''),
                    'quantity': float(item.get('shares', 0)),
                    'cost_basis': float(item.get('purchase_price', 0)) * float(item.get('shares', 0)),
                    'current_value': float(item.get('current_price', 0)) * float(item.get('shares', 0)),
                }
                portfolio_data.append(portfolio_item)
            
            metrics = polars_processor.calculate_portfolio_metrics(portfolio_data)
            assert isinstance(metrics, dict)
            assert 'total_value' in metrics
            assert 'total_return' in metrics
    
    def test_performance_comparison(self):
        """Test performance comparison between different libraries."""
        if not (POLARS_AVAILABLE and PANDAS_AVAILABLE):
            pytest.skip("Both Polars and Pandas needed for performance comparison")
        
        # Create larger dataset for meaningful performance comparison
        large_dataset = []
        for i in range(1000):
            large_dataset.append({
                'symbol': f'STOCK{i % 100}',
                'date': f'2024-01-{(i % 30) + 1:02d}',
                'close_price': 100 + (i * 0.1),
                'volume': 1000000 + i,
            })
        
        import time
        
        # Test Polars performance
        start_time = time.time()
        pl_df = pl.DataFrame(large_dataset)
        pl_df_filtered = pl_df.filter(pl.col('volume') > 1500000)
        polars_time = time.time() - start_time
        
        # Test Pandas performance
        start_time = time.time()
        pd_df = pd.DataFrame(large_dataset)
        pd_df_filtered = pd_df[pd_df['volume'] > 1500000]
        pandas_time = time.time() - start_time
        
        # Both should complete successfully (exact performance comparison depends on system)
        assert polars_time > 0
        assert pandas_time > 0
        
        # Log performance comparison
        logger.info(f"Performance comparison - Polars: {polars_time:.4f}s, Pandas: {pandas_time:.4f}s")


if __name__ == '__main__':
    # Run tests when file is executed directly
    pytest.main([__file__, '-v'])