"""Data validation utilities for DataProfiler compatibility.

This module provides comprehensive validation for data before it's passed to DataProfiler
to ensure compatibility and prevent constructor failures.
"""

import logging
from typing import Any, Union, List, Dict
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class ProfileDataError(Exception):
    """Exception raised when profile_data is not compatible with DataProfiler."""

    pass


def validate_profile_data(profile_data: Any) -> bool:
    """Validate that profile_data is compatible with DataProfiler constructor.

    DataProfiler can accept various data formats including:
    - pandas DataFrame
    - pandas Series
    - numpy arrays
    - Lists of dictionaries
    - CSV file paths (strings)
    - JSON data structures

    Args:
        profile_data: Data to be validated for DataProfiler compatibility

    Returns:
        bool: True if data is valid for DataProfiler

    Raises:
        ProfileDataError: If data is not compatible with DataProfiler

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
        >>> validate_profile_data(df)  # Returns True
        >>> validate_profile_data(None)  # Raises ProfileDataError
    """
    if profile_data is None:
        raise ProfileDataError("profile_data cannot be None")

    # Check for pandas DataFrame (most common and preferred format)
    if isinstance(profile_data, pd.DataFrame):
        return _validate_dataframe(profile_data)

    # Check for pandas Series
    if isinstance(profile_data, pd.Series):
        return _validate_series(profile_data)

    # Check for numpy arrays
    if isinstance(profile_data, np.ndarray):
        return _validate_numpy_array(profile_data)

    # Check for list of dictionaries (can be converted to DataFrame)
    if isinstance(profile_data, list):
        return _validate_list_data(profile_data)

    # Check for dictionary (single record or nested structure)
    if isinstance(profile_data, dict):
        return _validate_dict_data(profile_data)

    # Check for string (could be file path)
    if isinstance(profile_data, str):
        return _validate_string_data(profile_data)

    # If none of the above, it's not compatible
    raise ProfileDataError(
        "Unsupported data type: %s. "
        "DataProfiler supports pandas DataFrame/Series, numpy arrays, "
        "lists of dictionaries, or file paths.",
        type(profile_data).__name__,
    )


def _validate_dataframe(df: pd.DataFrame) -> bool:
    """Validate pandas DataFrame for DataProfiler compatibility.

    Args:
        df: pandas DataFrame to validate

    Returns:
        bool: True if DataFrame is valid

    Raises:
        ProfileDataError: If DataFrame is invalid
    """
    # Check for completely empty DataFrame (no rows and no columns)
    if len(df.columns) == 0 and len(df) == 0:
        raise ProfileDataError("DataFrame cannot be empty")

    # Check for DataFrame with columns but no rows
    if len(df) == 0:
        raise ProfileDataError("DataFrame cannot be empty")

    # Check for DataFrame with rows but no columns
    if len(df.columns) == 0:
        raise ProfileDataError("DataFrame must have at least one column")

    # Check for extremely large DataFrames that might cause memory issues
    if len(df) > 1_000_000 or len(df.columns) > 1000:
        logger.warning(
            "Large DataFrame detected: %s rows, %s columns. "
            "This may cause performance issues with DataProfiler.",
            len(df),
            len(df.columns),
        )

    # Check for problematic column names
    problematic_columns = []
    for col in df.columns:
        if not isinstance(col, (str, int, float)):
            problematic_columns.append(col)
        elif isinstance(col, str) and len(col.strip()) == 0:
            problematic_columns.append(col)

    if problematic_columns:
        raise ProfileDataError(
            f"DataFrame contains problematic column names: {problematic_columns}. "
            "Column names should be non-empty strings, integers, or floats."
        )

    logger.info(
        "DataFrame validation passed: %s rows, %s columns",
        len(df),
        len(df.columns),
    )
    return True


def _validate_series(series: pd.Series) -> bool:
    """Validate pandas Series for DataProfiler compatibility.

    Args:
        series: pandas Series to validate

    Returns:
        bool: True if Series is valid

    Raises:
        ProfileDataError: If Series is invalid
    """
    if series.empty:
        raise ProfileDataError("Series cannot be empty")

    if series.name is not None and not isinstance(
        series.name, (str, int, float)
    ):
        raise ProfileDataError(
            f"Series name must be a string, integer, or float, got: {type(series.name).__name__}"
        )

    logger.info("Series validation passed: %s values", len(series))
    return True


def _validate_numpy_array(arr: np.ndarray) -> bool:
    """Validate numpy array for DataProfiler compatibility.

    Args:
        arr: numpy array to validate

    Returns:
        bool: True if array is valid

    Raises:
        ProfileDataError: If array is invalid
    """
    if arr.size == 0:
        raise ProfileDataError("numpy array cannot be empty")

    # DataProfiler works best with 1D or 2D arrays
    if arr.ndim > 2:
        raise ProfileDataError(
            f"numpy array has {arr.ndim} dimensions. DataProfiler works best with 1D or 2D arrays."
        )

    # Check for unsupported dtypes
    if arr.dtype == np.object_ and arr.ndim > 1:
        logger.warning(
            "Multi-dimensional object arrays may cause issues with DataProfiler. "
            "Consider converting to DataFrame with explicit column types."
        )

    logger.info(
        "numpy array validation passed: shape {arr.shape}, dtype %s", arr.dtype
    )
    return True


def _validate_list_data(data: List[Any]) -> bool:
    """Validate list data for DataProfiler compatibility.

    Args:
        data: List to validate

    Returns:
        bool: True if list is valid

    Raises:
        ProfileDataError: If list is invalid
    """
    if len(data) == 0:
        raise ProfileDataError("List cannot be empty")

    # Check if it's a list of dictionaries (records format)
    if all(isinstance(item, dict) for item in data):
        return _validate_records_format(data)

    # Check if it's a simple list of values
    if all(not isinstance(item, (dict, list)) for item in data):
        logger.info("Simple list validation passed: %s items", len(data))
        return True

    # Mixed types or nested structures might be problematic
    unique_types = {type(item).__name__ for item in data}
    if len(unique_types) > 3:  # Allow some type diversity
        logger.warning(
            "List contains many different types: %s. "
            "This may cause issues with DataProfiler.",
            unique_types,
        )

    logger.info("List validation passed: %s items", len(data))
    return True


def _validate_records_format(records: List[Dict[str, Any]]) -> bool:
    """Validate list of dictionaries (records format).

    Args:
        records: List of dictionaries to validate

    Returns:
        bool: True if records are valid

    Raises:
        ProfileDataError: If records are invalid
    """
    if not records:
        raise ProfileDataError("Records list cannot be empty")

    # Check that all records have the same keys (consistent schema)
    first_keys = set(records[0].keys())
    for i, record in enumerate(records[1:], 1):
        record_keys = set(record.keys())
        if record_keys != first_keys:
            missing_keys = first_keys - record_keys
            extra_keys = record_keys - first_keys
            error_msg = f"Inconsistent schema at record {i}."
            if missing_keys:
                error_msg += f" Missing keys: {missing_keys}."
            if extra_keys:
                error_msg += f" Extra keys: {extra_keys}."
            raise ProfileDataError(error_msg)

    # Check for empty key names
    for key in first_keys:
        if not isinstance(key, str) or len(key.strip()) == 0:
            raise ProfileDataError(
                f"Invalid key name: '{key}'. Keys must be non-empty strings."
            )

    logger.info(
        "Records validation passed: %s records with %s fields",
        len(records),
        len(first_keys),
    )
    return True


def _validate_dict_data(data: Dict[str, Any]) -> bool:
    """Validate dictionary data for DataProfiler compatibility.

    Args:
        data: Dictionary to validate

    Returns:
        bool: True if dictionary is valid

    Raises:
        ProfileDataError: If dictionary is invalid
    """
    if not data:
        raise ProfileDataError("Dictionary cannot be empty")

    # Check if it looks like a single record
    if all(
        not isinstance(value, (list, dict, np.ndarray))
        for value in data.values()
    ):
        logger.info("Dictionary appears to be a single record")
        return True

    # Check if it's column-oriented data (dict of lists/arrays)
    list_lengths = []
    for key, value in data.items():
        if isinstance(value, (list, np.ndarray, pd.Series)):
            list_lengths.append(len(value))
        elif not isinstance(value, (dict, list)):
            # Scalar values are ok for single records
            continue
        else:
            logger.warning(
                "Complex nested structure detected in key '%s'", key
            )

    # If we have lists/arrays, they should all be the same length
    if list_lengths and len(set(list_lengths)) > 1:
        raise ProfileDataError(
            f"Inconsistent lengths in dictionary arrays: {dict(zip(data.keys(), list_lengths))}"
        )

    logger.info("Dictionary validation passed: %s keys", len(data))
    return True


def _validate_string_data(data: str) -> bool:
    """Validate string data (assumed to be file path) for DataProfiler compatibility.

    Args:
        data: String to validate (assumed to be file path)

    Returns:
        bool: True if string is valid

    Raises:
        ProfileDataError: If string is invalid
    """
    if len(data.strip()) == 0:
        raise ProfileDataError("File path cannot be empty")

    # Check for common file extensions that DataProfiler supports
    supported_extensions = {".csv", ".json", ".parquet", ".xlsx", ".txt"}
    data_lower = data.lower()

    has_supported_extension = any(
        data_lower.endswith(ext) for ext in supported_extensions
    )

    if not has_supported_extension:
        logger.warning(
            "File path '%s' does not have a recognized extension. "
            "Supported extensions: %s",
            data,
            supported_extensions,
        )

    # Note: We don't check if file exists here since DataProfiler will handle that
    # and this validation might be called before the file is created

    logger.info("File path validation passed: '%s'", data)
    return True


def validate_and_prepare_data(
    profile_data: Any,
) -> Union[pd.DataFrame, pd.Series, np.ndarray, str]:
    """Validate and optionally prepare data for DataProfiler.

    This function not only validates the data but can also perform basic
    preprocessing to optimize it for DataProfiler usage.

    Args:
        profile_data: Data to validate and prepare

    Returns:
        Validated and potentially optimized data

    Raises:
        ProfileDataError: If data is not compatible
    """
    # If it's a list of dictionaries, try to convert to DataFrame for better performance
    if (
        isinstance(profile_data, list)
        and profile_data
        and isinstance(profile_data[0], dict)
    ):
        try:
            # First try to validate as records format to check schema consistency
            validate_profile_data(profile_data)
            # If validation passes, convert to DataFrame
            df = pd.DataFrame(profile_data)
            logger.info("Converted list of dictionaries to pandas DataFrame")
            return df
        except ProfileDataError:
            # If validation fails (e.g., inconsistent schema), return original data with warning
            logger.warning(
                "Failed to validate data structure. Using original data."
            )
            return profile_data

    # For all other cases, validate first then process
    validate_profile_data(profile_data)

    # If it's a dictionary with consistent list values, convert to DataFrame
    if isinstance(profile_data, dict):
        try:
            # Check if all values are lists/arrays of the same length
            list_values = {
                k: v
                for k, v in profile_data.items()
                if isinstance(v, (list, np.ndarray, pd.Series))
            }
            if list_values:
                lengths = [len(v) for v in list_values.values()]
                if len(set(lengths)) == 1:  # All same length
                    df = pd.DataFrame(profile_data)
                    logger.info("Converted dictionary to pandas DataFrame")
                    return df
        except Exception as e:
            logger.warning(
                "Failed to convert dictionary to DataFrame: %s. Using original data.",
                e,
            )

    return profile_data
