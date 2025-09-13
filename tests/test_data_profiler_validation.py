"""Tests for DataProfiler validation functionality."""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

from personal_finance.data_profiler.validators import (
    validate_profile_data,
    validate_and_prepare_data,
    ProfileDataError,
    _validate_dataframe,
    _validate_series,
    _validate_numpy_array,
    _validate_list_data,
    _validate_dict_data,
    _validate_string_data,
    _validate_records_format
)


class TestValidateProfileData:
    """Test cases for profile data validation."""
    
    def test_validate_none_data_raises_error(self):
        """Test that None data raises ProfileDataError."""
        with pytest.raises(ProfileDataError, match="profile_data cannot be None"):
            validate_profile_data(None)
    
    def test_validate_valid_dataframe(self):
        """Test validation of valid DataFrame."""
        df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c'],
            'col3': [1.1, 2.2, 3.3]
        })
        assert validate_profile_data(df) is True
    
    def test_validate_empty_dataframe_raises_error(self):
        """Test that empty DataFrame raises ProfileDataError."""
        df = pd.DataFrame()
        with pytest.raises(ProfileDataError, match="DataFrame cannot be empty"):
            validate_profile_data(df)
    
    def test_validate_dataframe_no_columns_raises_error(self):
        """Test that DataFrame with no columns raises ProfileDataError."""
        df = pd.DataFrame(index=[0, 1, 2])
        with pytest.raises(ProfileDataError, match="DataFrame must have at least one column"):
            validate_profile_data(df)
    
    def test_validate_valid_series(self):
        """Test validation of valid Series."""
        series = pd.Series([1, 2, 3, 4, 5])
        assert validate_profile_data(series) is True
    
    def test_validate_empty_series_raises_error(self):
        """Test that empty Series raises ProfileDataError."""
        series = pd.Series([], dtype='float64')
        with pytest.raises(ProfileDataError, match="Series cannot be empty"):
            validate_profile_data(series)
    
    def test_validate_valid_numpy_array(self):
        """Test validation of valid numpy array."""
        arr = np.array([1, 2, 3, 4, 5])
        assert validate_profile_data(arr) is True
    
    def test_validate_2d_numpy_array(self):
        """Test validation of 2D numpy array."""
        arr = np.array([[1, 2], [3, 4], [5, 6]])
        assert validate_profile_data(arr) is True
    
    def test_validate_empty_numpy_array_raises_error(self):
        """Test that empty numpy array raises ProfileDataError."""
        arr = np.array([])
        with pytest.raises(ProfileDataError, match="numpy array cannot be empty"):
            validate_profile_data(arr)
    
    def test_validate_high_dimension_array_raises_error(self):
        """Test that high-dimensional arrays raise ProfileDataError."""
        arr = np.zeros((2, 2, 2, 2))  # 4D array
        with pytest.raises(ProfileDataError, match="numpy array has 4 dimensions"):
            validate_profile_data(arr)
    
    def test_validate_list_of_dicts(self):
        """Test validation of list of dictionaries."""
        data = [
            {'name': 'John', 'age': 30, 'amount': 100.0},
            {'name': 'Jane', 'age': 25, 'amount': 200.0},
            {'name': 'Bob', 'age': 35, 'amount': 150.0}
        ]
        assert validate_profile_data(data) is True
    
    def test_validate_simple_list(self):
        """Test validation of simple list."""
        data = [1, 2, 3, 4, 5]
        assert validate_profile_data(data) is True
    
    def test_validate_empty_list_raises_error(self):
        """Test that empty list raises ProfileDataError."""
        with pytest.raises(ProfileDataError, match="List cannot be empty"):
            validate_profile_data([])
    
    def test_validate_inconsistent_dict_list_raises_error(self):
        """Test that inconsistent dictionary list raises ProfileDataError."""
        data = [
            {'name': 'John', 'age': 30},
            {'name': 'Jane', 'salary': 50000}  # Different keys
        ]
        with pytest.raises(ProfileDataError, match="Inconsistent schema"):
            validate_profile_data(data)
    
    def test_validate_single_dict(self):
        """Test validation of single dictionary."""
        data = {'name': 'John', 'age': 30, 'amount': 100.0}
        assert validate_profile_data(data) is True
    
    def test_validate_column_oriented_dict(self):
        """Test validation of column-oriented dictionary."""
        data = {
            'names': ['John', 'Jane', 'Bob'],
            'ages': [30, 25, 35],
            'amounts': [100.0, 200.0, 150.0]
        }
        assert validate_profile_data(data) is True
    
    def test_validate_inconsistent_dict_lengths_raises_error(self):
        """Test that dictionary with inconsistent lengths raises error."""
        data = {
            'names': ['John', 'Jane'],
            'ages': [30, 25, 35]  # Different length
        }
        with pytest.raises(ProfileDataError, match="Inconsistent lengths"):
            validate_profile_data(data)
    
    def test_validate_file_path_string(self):
        """Test validation of file path string."""
        assert validate_profile_data('/path/to/data.csv') is True
        assert validate_profile_data('data.json') is True
        assert validate_profile_data('financial_data.xlsx') is True
    
    def test_validate_empty_string_raises_error(self):
        """Test that empty string raises ProfileDataError."""
        with pytest.raises(ProfileDataError, match="File path cannot be empty"):
            validate_profile_data("")
        with pytest.raises(ProfileDataError, match="File path cannot be empty"):
            validate_profile_data("   ")
    
    def test_validate_unsupported_type_raises_error(self):
        """Test that unsupported data types raise ProfileDataError."""
        with pytest.raises(ProfileDataError, match="Unsupported data type"):
            validate_profile_data(set([1, 2, 3]))
        with pytest.raises(ProfileDataError, match="Unsupported data type"):
            validate_profile_data(42)


class TestDataFrameValidation:
    """Test cases specifically for DataFrame validation."""
    
    def test_validate_large_dataframe_warning(self, caplog):
        """Test that large DataFrames generate warnings."""
        # Create a large DataFrame (using smaller size for test efficiency)
        large_df = pd.DataFrame({
            f'col_{i}': range(1000) for i in range(10)
        })
        
        with patch('personal_finance.data_profiler.validators.logger') as mock_logger:
            result = _validate_dataframe(large_df)
            assert result is True
            mock_logger.info.assert_called_with(f"DataFrame validation passed: {len(large_df)} rows, {len(large_df.columns)} columns")
    
    def test_validate_problematic_column_names(self):
        """Test validation of DataFrames with problematic column names."""
        # Empty string column name
        df_empty_col = pd.DataFrame({
            'good_col': [1, 2, 3],
            '': [4, 5, 6]
        })
        with pytest.raises(ProfileDataError, match="problematic column names"):
            _validate_dataframe(df_empty_col)
        
        # Non-string/int/float column name
        df_bad_col = pd.DataFrame({
            'good_col': [1, 2, 3],
            tuple([1, 2]): [4, 5, 6]
        })
        with pytest.raises(ProfileDataError, match="problematic column names"):
            _validate_dataframe(df_bad_col)


class TestSeriesValidation:
    """Test cases specifically for Series validation."""
    
    def test_validate_series_with_name(self):
        """Test validation of Series with valid name."""
        series = pd.Series([1, 2, 3], name='valid_name')
        assert _validate_series(series) is True
    
    def test_validate_series_invalid_name_raises_error(self):
        """Test that Series with invalid name raises error."""
        series = pd.Series([1, 2, 3], name=['invalid', 'name'])
        with pytest.raises(ProfileDataError, match="Series name must be"):
            _validate_series(series)


class TestListValidation:
    """Test cases specifically for list validation."""
    
    def test_validate_records_format_empty_raises_error(self):
        """Test that empty records list raises error."""
        with pytest.raises(ProfileDataError, match="Records list cannot be empty"):
            _validate_records_format([])
    
    def test_validate_records_format_invalid_keys(self):
        """Test validation of records with invalid keys."""
        records = [
            {'': 'value1', 'valid_key': 'value2'},
            {'': 'value3', 'valid_key': 'value4'}
        ]
        with pytest.raises(ProfileDataError, match="Invalid key name"):
            _validate_records_format(records)


class TestValidateAndPrepareData:
    """Test cases for the validation and preparation function."""
    
    def test_prepare_list_of_dicts_to_dataframe(self):
        """Test conversion of list of dicts to DataFrame."""
        data = [
            {'name': 'John', 'age': 30},
            {'name': 'Jane', 'age': 25}
        ]
        result = validate_and_prepare_data(data)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert list(result.columns) == ['name', 'age']
    
    def test_prepare_column_dict_to_dataframe(self):
        """Test conversion of column-oriented dict to DataFrame."""
        data = {
            'names': ['John', 'Jane'],
            'ages': [30, 25]
        }
        result = validate_and_prepare_data(data)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert list(result.columns) == ['names', 'ages']
    
    def test_prepare_data_conversion_failure_returns_original(self, caplog):
        """Test that conversion failure returns original data."""
        # Create data that will fail DataFrame conversion
        data = [
            {'name': 'John'},
            {'different_key': 'Jane'}  # Inconsistent keys
        ]
        
        with patch('personal_finance.data_profiler.validators.logger') as mock_logger:
            result = validate_and_prepare_data(data)
            # Should return original data if conversion fails
            assert result == data
            mock_logger.warning.assert_called()
    
    def test_prepare_data_no_conversion_needed(self):
        """Test that data needing no conversion is returned as-is."""
        df = pd.DataFrame({'col1': [1, 2, 3]})
        result = validate_and_prepare_data(df)
        assert result is df  # Same object
        
        series = pd.Series([1, 2, 3])
        result = validate_and_prepare_data(series)
        assert result is series  # Same object


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_profile_data_error_inheritance(self):
        """Test that ProfileDataError is properly inheritable from Exception."""
        error = ProfileDataError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"
    
    @pytest.mark.parametrize("invalid_data", [
        float('inf'),
        float('-inf'),
        complex(1, 2),
        lambda x: x,
        Exception("test")
    ])
    def test_validate_various_invalid_types(self, invalid_data):
        """Test validation of various invalid data types."""
        with pytest.raises(ProfileDataError):
            validate_profile_data(invalid_data)


class TestFilePathValidation:
    """Test cases specifically for file path validation."""
    
    @pytest.mark.parametrize("file_path", [
        "data.csv",
        "/path/to/data.json",
        "financial_data.xlsx",
        "dataset.parquet",
        "log_file.txt"
    ])
    def test_validate_supported_file_extensions(self, file_path):
        """Test validation of supported file extensions."""
        assert _validate_string_data(file_path) is True
    
    def test_validate_unsupported_extension_warning(self, caplog):
        """Test that unsupported extensions generate warnings."""
        with patch('personal_finance.data_profiler.validators.logger') as mock_logger:
            result = _validate_string_data("data.unknown")
            assert result is True
            mock_logger.warning.assert_called()


# Integration tests
class TestIntegrationScenarios:
    """Integration test scenarios with realistic financial data."""
    
    def test_validate_financial_dataframe(self):
        """Test validation of realistic financial DataFrame."""
        financial_df = pd.DataFrame({
            'transaction_id': ['T001', 'T002', 'T003'],
            'amount': [100.50, 250.75, 75.25],
            'transaction_type': ['debit', 'credit', 'debit'],
            'account_id': ['ACC001', 'ACC002', 'ACC001'],
            'transaction_date': pd.to_datetime(['2024-01-15', '2024-01-16', '2024-01-17'])
        })
        assert validate_profile_data(financial_df) is True
    
    def test_validate_portfolio_data(self):
        """Test validation of portfolio data structure."""
        portfolio_data = [
            {
                'symbol': 'AAPL',
                'quantity': 100,
                'purchase_price': 150.25,
                'current_price': 175.50,
                'purchase_date': '2024-01-01'
            },
            {
                'symbol': 'GOOGL',
                'quantity': 50,
                'purchase_price': 2800.75,
                'current_price': 2950.25,
                'purchase_date': '2024-01-02'
            }
        ]
        assert validate_profile_data(portfolio_data) is True
        
        # Test conversion to DataFrame
        result = validate_and_prepare_data(portfolio_data)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'symbol' in result.columns
    
    def test_validate_price_history_array(self):
        """Test validation of price history numpy array."""
        # Simulate OHLCV data
        price_data = np.array([
            [150.0, 155.0, 148.0, 152.0, 1000000],  # Open, High, Low, Close, Volume
            [152.0, 157.0, 150.0, 155.0, 1200000],
            [155.0, 160.0, 153.0, 158.0, 950000]
        ])
        assert validate_profile_data(price_data) is True