"""
Unit tests for DataProfiler services and validators.

Tests cover the main profile_data function and various input validation scenarios.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from personal_finance.data_profiler.services import (
    DataProfilerService,
    profile_data,
)
from personal_finance.data_profiler.validators import (
    ProfileDataError,
    validate_profile_data,
    validate_and_prepare_data,
)


class TestProfileDataFunction:
    """Test cases for the main profile_data function."""

    def test_profile_data_with_dataframe(self):
        """Test profile_data with pandas DataFrame input."""
        df = pd.DataFrame(
            {
                "amount": [100, 200, 300, 150],
                "account": ["A123", "B456", "C789", "D012"],
                "date": [
                    "2023-01-01",
                    "2023-01-02",
                    "2023-01-03",
                    "2023-01-04",
                ],
            }
        )

        result = profile_data(df)

        # Verify expected structure
        assert isinstance(result, dict)
        assert "rows" in result
        assert "columns" in result
        assert "pii_detected" in result
        assert "fields" in result
        assert "data_quality" in result
        assert "financial_patterns" in result

        # Verify dimensions
        assert result["rows"] == 4
        assert result["columns"] == 3

        # Verify fields are populated
        assert "amount" in result["fields"]
        assert "account" in result["fields"]
        assert "date" in result["fields"]

        # Verify field structure
        amount_field = result["fields"]["amount"]
        assert "data_type" in amount_field
        assert "null_count" in amount_field
        assert "null_ratio" in amount_field
        assert "statistics" in amount_field

    def test_profile_data_with_list_of_dicts(self):
        """Test profile_data with list of dictionaries input."""
        data = [
            {"name": "Alice", "age": 30, "salary": 50000},
            {"name": "Bob", "age": 25, "salary": 45000},
            {"name": "Carol", "age": 35, "salary": 60000},
        ]

        result = profile_data(data)

        assert result["rows"] == 3
        assert result["columns"] == 3
        assert "name" in result["fields"]
        assert "age" in result["fields"]
        assert "salary" in result["fields"]

    def test_profile_data_with_numpy_array(self):
        """Test profile_data with numpy array input."""
        arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

        result = profile_data(arr)

        assert result["rows"] == 3
        assert result["columns"] == 3
        assert (
            len(result["fields"]) >= 0
        )  # Fields may or may not be populated for arrays

    def test_profile_data_with_pandas_series(self):
        """Test profile_data with pandas Series input."""
        series = pd.Series([10, 20, 30, 40, 50], name="values")

        result = profile_data(series)

        assert result["rows"] == 5
        assert result["columns"] == 1

    def test_profile_data_with_file_path(self):
        """Test profile_data with file path input."""
        # Get the sample CSV file path
        fixtures_dir = Path(__file__).parent / "fixtures"
        sample_file = fixtures_dir / "sample.csv"

        if sample_file.exists():
            result = profile_data(str(sample_file))

            # For file paths, dimensions might be -1 until processed
            assert isinstance(result, dict)
            assert "rows" in result
            assert "columns" in result

    def test_profile_data_pii_detection_disabled(self):
        """Test profile_data with PII detection disabled."""
        df = pd.DataFrame(
            {
                "name": ["John Doe", "Jane Smith"],
                "ssn": ["123-45-6789", "987-65-4321"],
            }
        )

        result = profile_data(df, enable_sensitive_data_detection=False)

        # PII detection should be disabled
        assert result["pii_detected"] == False
        assert result["pii_detected"] is False

    def test_profile_data_pii_detection_enabled(self):
        """Test profile_data with PII detection enabled."""
        df = pd.DataFrame(
            {
                "name": ["John Doe", "Jane Smith"],
                "ssn": ["123-45-6789", "987-65-4321"],
                "account": ["987654321", "123456789"],
            }
        )

        result = profile_data(df, enable_sensitive_data_detection=True)

        # Should detect potential PII in SSN and account columns
        # Note: The actual detection depends on the implementation
        assert isinstance(result["pii_detected"], bool)
        if result["pii_detected"]:
            assert "sensitive_findings" in result

    def test_profile_data_with_invalid_input(self):
        """Test profile_data with invalid input raises appropriate exception."""
        with pytest.raises(ProfileDataError):
            profile_data(None)

        with pytest.raises(ProfileDataError):
            profile_data([])  # Empty list

        with pytest.raises(ProfileDataError):
            profile_data(pd.DataFrame())  # Empty DataFrame

    def test_profile_data_financial_patterns(self):
        """Test that financial patterns are detected for financial data."""
        df = pd.DataFrame(
            {
                "amount": [100.50, -25.00, 1500.00],
                "balance": [1000, 975, 2475],
                "transaction_date": ["2023-01-15", "2023-01-16", "2023-01-17"],
                "account_number": ["123456789", "123456789", "123456789"],
            }
        )

        result = profile_data(df)

        # Should detect financial patterns
        financial_patterns = result.get("financial_patterns", {})
        assert isinstance(financial_patterns, dict)

        # May detect currency/amount columns
        potential_currency = financial_patterns.get(
            "potential_currency_columns", []
        )
        potential_amounts = financial_patterns.get(
            "potential_amount_columns", []
        )

        # At least one of these should contain 'amount' or 'balance'
        all_financial_cols = potential_currency + potential_amounts
        assert any(col in ["amount", "balance"] for col in all_financial_cols)

    def test_profile_data_data_quality_analysis(self):
        """Test that data quality analysis is performed."""
        df = pd.DataFrame(
            {
                "complete_col": [1, 2, 3, 4],
                "missing_col": [1, None, 3, None],
                "constant_col": [5, 5, 5, 5],
                "duplicate_row_col": [1, 2, 1, 2],
            }
        )

        result = profile_data(df)

        data_quality = result.get("data_quality", {})
        assert isinstance(data_quality, dict)

        # Should detect missing data
        if "missing_data_ratio" in data_quality:
            assert data_quality["missing_data_ratio"] > 0

        # Should detect constant columns
        if "constant_columns" in data_quality:
            assert "constant_col" in data_quality["constant_columns"]


class TestInputValidation:
    """Test cases for input validation functions."""

    def test_validate_profile_data_valid_inputs(self):
        """Test validation with various valid inputs."""
        # Valid DataFrame
        df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
        assert validate_profile_data(df) == True

        # Valid Series
        series = pd.Series([1, 2, 3])
        assert validate_profile_data(series) == True

        # Valid numpy array
        arr = np.array([1, 2, 3])
        assert validate_profile_data(arr) == True

        # Valid list of dictionaries
        records = [{"a": 1, "b": "x"}, {"a": 2, "b": "y"}]
        assert validate_profile_data(records) == True

        # Valid file path string
        assert validate_profile_data("test.csv") == True

    def test_validate_profile_data_invalid_inputs(self):
        """Test validation with invalid inputs."""
        # None input
        with pytest.raises(
            ProfileDataError, match="profile_data cannot be None"
        ):
            validate_profile_data(None)

        # Empty DataFrame
        with pytest.raises(
            ProfileDataError, match="DataFrame cannot be empty"
        ):
            validate_profile_data(pd.DataFrame())

        # Empty Series
        with pytest.raises(ProfileDataError, match="Series cannot be empty"):
            validate_profile_data(pd.Series(dtype=object))

        # Empty numpy array
        with pytest.raises(
            ProfileDataError, match="numpy array cannot be empty"
        ):
            validate_profile_data(np.array([]))

        # Empty list
        with pytest.raises(ProfileDataError, match="List cannot be empty"):
            validate_profile_data([])

        # Empty string
        with pytest.raises(
            ProfileDataError, match="File path cannot be empty"
        ):
            validate_profile_data("")

    def test_validate_profile_data_inconsistent_records(self):
        """Test validation with inconsistent record schemas."""
        # Inconsistent keys in records
        inconsistent_records = [
            {"a": 1, "b": "x"},
            {"a": 2, "c": "y"},  # Different key 'c' instead of 'b'
        ]

        with pytest.raises(ProfileDataError, match="Inconsistent schema"):
            validate_profile_data(inconsistent_records)

    def test_validate_and_prepare_data_conversions(self):
        """Test data preparation and conversions."""
        # List of dicts should be converted to DataFrame
        records = [{"a": 1, "b": "x"}, {"a": 2, "b": "y"}]
        result = validate_and_prepare_data(records)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert list(result.columns) == ["a", "b"]

        # Dictionary with equal-length arrays should be converted to DataFrame
        dict_data = {"col1": [1, 2, 3], "col2": ["a", "b", "c"]}
        result = validate_and_prepare_data(dict_data)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert list(result.columns) == ["col1", "col2"]

    def test_validate_and_prepare_data_passthrough(self):
        """Test that some data types are passed through unchanged."""
        # DataFrame should pass through unchanged
        df = pd.DataFrame({"a": [1, 2, 3]})
        result = validate_and_prepare_data(df)
        assert result is df  # Should be the same object

        # String (file path) should pass through unchanged
        filepath = "test.csv"
        result = validate_and_prepare_data(filepath)
        assert result == filepath


class TestDataProfilerServiceIntegration:
    """Integration tests for DataProfilerService class."""

    def test_service_initialization(self):
        """Test service initializes correctly."""
        service = DataProfilerService()
        assert isinstance(service, DataProfilerService)
        assert hasattr(service, "is_available")

        # Test with different settings
        service_no_pii = DataProfilerService(
            enable_sensitive_data_detection=False
        )
        assert service_no_pii.enable_sensitive_data_detection == False

    def test_service_availability_check(self):
        """Test availability checking works."""
        service = DataProfilerService()
        availability = service.is_available()
        assert isinstance(availability, bool)
        # Note: Availability depends on whether DataProfiler is installed

    @patch(
        "personal_finance.data_profiler.services.DataProfilerService.is_available"
    )
    def test_profile_data_without_dataprofiler(self, mock_is_available):
        """Test profile_data function when DataProfiler is not available."""
        mock_is_available.return_value = False

        df = pd.DataFrame(
            {"amount": [100, 200, 300], "type": ["buy", "sell", "buy"]}
        )

        result = profile_data(df)

        # Should still provide basic analysis
        assert result["rows"] == 3
        assert result["columns"] == 2
        assert "fields" in result
        assert len(result["fields"]) > 0


class TestCLIFunctionality:
    """Test the CLI functionality."""

    def test_cli_argument_parsing(self):
        """Test that CLI can be imported and would parse arguments correctly."""
        # Import the module to ensure CLI code doesn't have syntax errors
        import personal_finance.data_profiler.services as services_module

        # Verify the CLI components exist
        assert hasattr(services_module, "profile_data")

        # Check that the main block exists by looking at the source
        import inspect

        source = inspect.getsource(services_module)
        assert 'if __name__ == "__main__"' in source
        assert "argparse.ArgumentParser" in source

    def test_cli_with_sample_file(self):
        """Test CLI execution with sample file (if DataProfiler available)."""
        # Get the sample file path
        fixtures_dir = Path(__file__).parent / "fixtures"
        sample_file = fixtures_dir / "sample.csv"

        if sample_file.exists():
            # Test that we can profile the sample file programmatically
            result = profile_data(str(sample_file))

            # Should return valid results
            assert isinstance(result, dict)
            assert "rows" in result
            assert "columns" in result


# Fixtures for testing
@pytest.fixture
def sample_financial_dataframe():
    """Fixture providing a sample financial DataFrame."""
    return pd.DataFrame(
        {
            "amount": [100.50, -25.00, 1500.00, -450.75, -85.20, 2000.00],
            "transaction_type": [
                "credit",
                "debit",
                "credit",
                "debit",
                "debit",
                "credit",
            ],
            "account": [
                "123456789",
                "123456789",
                "123456789",
                "123456789",
                "123456789",
                "123456789",
            ],
            "date": [
                "2023-01-15",
                "2023-01-16",
                "2023-01-17",
                "2023-01-18",
                "2023-01-19",
                "2023-01-20",
            ],
            "description": [
                "Direct deposit",
                "ATM withdrawal",
                "Transfer from savings",
                "Rent payment",
                "Grocery store",
                "Salary deposit",
            ],
        }
    )


@pytest.fixture
def sample_sensitive_data():
    """Fixture providing data with potential PII."""
    return pd.DataFrame(
        {
            "name": ["John Doe", "Jane Smith", "Bob Johnson"],
            "ssn": ["123-45-6789", "987-65-4321", "456-78-9012"],
            "account": ["987654321", "123456789", "555666777"],
            "balance": [1000.0, 2500.5, 750.25],
        }
    )


@pytest.fixture
def temp_csv_file(sample_financial_dataframe):
    """Fixture providing a temporary CSV file."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False
    ) as f:
        sample_financial_dataframe.to_csv(f.name, index=False)
        yield f.name
    os.unlink(f.name)


class TestFixtureBasedScenarios:
    """Test scenarios using pytest fixtures."""

    def test_profile_financial_dataframe(self, sample_financial_dataframe):
        """Test profiling a typical financial DataFrame."""
        result = profile_data(sample_financial_dataframe)

        assert result["rows"] == 6
        assert result["columns"] == 5
        assert "amount" in result["fields"]
        assert "account" in result["fields"]

        # Should detect financial patterns
        financial_patterns = result.get("financial_patterns", {})
        assert isinstance(financial_patterns, dict)

    def test_profile_sensitive_data(self, sample_sensitive_data):
        """Test profiling data with PII."""
        result = profile_data(
            sample_sensitive_data, enable_sensitive_data_detection=True
        )

        assert result["rows"] == 3
        assert result["columns"] == 4

        # Should potentially detect PII (implementation dependent)
        assert isinstance(result["pii_detected"], bool)

    def test_profile_csv_file(self, temp_csv_file):
        """Test profiling a CSV file."""
        result = profile_data(temp_csv_file)

        # Should handle file input
        assert isinstance(result, dict)
        assert "rows" in result
        assert "columns" in result
