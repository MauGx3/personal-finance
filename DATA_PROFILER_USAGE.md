# Data Profiling with DataProfiler Integration

This document describes the new DataProfiler integration module that provides safe data profiling with comprehensive validation to prevent constructor failures.

## Overview

The `personal_finance.data_profiler` module provides:

- **Data Validation**: Comprehensive validation of data before passing to DataProfiler
- **Sensitive Data Detection**: Financial-specific PII and sensitive data detection
- **Data Quality Analysis**: Analysis of data quality issues and patterns
- **Safe Integration**: Graceful handling when DataProfiler is not available

## Quick Start

### Basic Validation

```python
from personal_finance.data_profiler import validate_profile_data, ProfileDataError
import pandas as pd

# Validate DataFrame before profiling
financial_df = pd.DataFrame({
    'transaction_id': ['TXN001', 'TXN002'],
    'amount': [100.50, 250.75],
    'account_id': ['ACC001', 'ACC002']
})

try:
    validate_profile_data(financial_df)
    print("✓ Data is valid for DataProfiler")
except ProfileDataError as e:
    print(f"✗ Validation failed: {e}")
```

### Using the DataProfiler Service

```python
from personal_finance.data_profiler import DataProfilerService

# Initialize service with sensitive data detection
service = DataProfilerService(enable_sensitive_data_detection=True)

# Analyze financial data
analysis = service.analyze_financial_data(financial_df)

print("Financial patterns:", analysis['financial_patterns'])
print("Data quality:", analysis['data_quality'])
print("Sensitive data:", analysis['sensitive_data_detected'])
```

## Supported Data Formats

The validation system supports all DataProfiler-compatible formats:

### 1. Pandas DataFrame (Recommended)
```python
df = pd.DataFrame({
    'symbol': ['AAPL', 'GOOGL'],
    'price': [175.50, 2950.25],
    'volume': [1000000, 800000]
})
validate_profile_data(df)  # ✓ Valid
```

### 2. Pandas Series
```python
series = pd.Series([100, 200, 300], name='amounts')
validate_profile_data(series)  # ✓ Valid
```

### 3. NumPy Arrays
```python
import numpy as np
price_array = np.array([[100, 200], [300, 400]])
validate_profile_data(price_array)  # ✓ Valid
```

### 4. List of Dictionaries (Records Format)
```python
portfolio_records = [
    {'symbol': 'AAPL', 'quantity': 100, 'price': 150.25},
    {'symbol': 'GOOGL', 'quantity': 50, 'price': 2800.75}
]
validate_profile_data(portfolio_records)  # ✓ Valid
```

### 5. Column-Oriented Dictionary
```python
price_data = {
    'dates': ['2024-01-01', '2024-01-02'],
    'prices': [100.0, 102.5],
    'volumes': [1000000, 1200000]
}
validate_profile_data(price_data)  # ✓ Valid
```

### 6. File Paths
```python
validate_profile_data('/path/to/financial_data.csv')  # ✓ Valid
validate_profile_data('portfolio.xlsx')              # ✓ Valid
```

## Validation Rules

### DataFrame Validation
- Must not be empty
- Must have at least one column
- Column names must be strings, integers, or floats
- No empty string column names
- Warns for extremely large DataFrames (>1M rows or >1000 columns)

### Series Validation
- Must not be empty
- Series name (if provided) must be string, integer, or float

### NumPy Array Validation
- Must not be empty
- Maximum 2 dimensions (DataProfiler limitation)
- Warns for object arrays with multiple dimensions

### List Validation
- Must not be empty
- For list of dictionaries: consistent schema across all records
- For simple lists: allows mixed types with warnings for excessive diversity

### Dictionary Validation
- Must not be empty
- For column-oriented data: all arrays/lists must have same length
- For record data: validates as single record

### String Validation (File Paths)
- Must not be empty or whitespace-only
- Warns for unsupported file extensions
- Supported extensions: .csv, .json, .parquet, .xlsx, .txt

## Error Handling

### ProfileDataError Exception
```python
try:
    validate_profile_data(invalid_data)
except ProfileDataError as e:
    print(f"Validation failed: {e}")
    # Handle the error appropriately
```

### Common Error Cases
```python
# Empty data
validate_profile_data(pd.DataFrame())  # Raises: DataFrame cannot be empty

# None data
validate_profile_data(None)  # Raises: profile_data cannot be None

# Inconsistent records
validate_profile_data([
    {'name': 'John', 'age': 30},
    {'name': 'Jane', 'salary': 50000}  # Different keys
])  # Raises: Inconsistent schema

# Unsupported type
validate_profile_data(set([1, 2, 3]))  # Raises: Unsupported data type
```

## Financial Data Analysis

The `DataProfilerService` provides financial-specific analysis:

### Pattern Detection
```python
analysis = service.analyze_financial_data(financial_df)

patterns = analysis['financial_patterns']
# - potential_currency_columns: Columns that look like currency/amounts
# - potential_date_columns: Columns that look like dates
# - potential_amount_columns: Numeric columns for financial amounts
# - suspicious_patterns: Unusual patterns that may indicate data issues
```

### Data Quality Analysis
```python
quality = analysis['data_quality']
# - missing_data_ratio: Proportion of missing values
# - duplicate_rows: Number of duplicate rows
# - empty_columns: Columns with all null values
# - constant_columns: Columns with only one unique value
# - outlier_candidates: Columns with potential outliers
```

### Sensitive Data Detection
```python
sensitive_data = analysis['sensitive_data_detected']
# Detects:
# - potential_account_number: Numeric strings that look like account numbers
# - potential_ssn: Patterns matching Social Security Numbers
# Each finding includes confidence level and recommendations
```

## Data Preparation

The `validate_and_prepare_data` function optimizes data for DataProfiler:

```python
from personal_finance.data_profiler import validate_and_prepare_data

# Converts list of dicts to DataFrame for better performance
records = [{'id': 1, 'amount': 100}, {'id': 2, 'amount': 200}]
optimized_data = validate_and_prepare_data(records)
# Returns: pandas DataFrame

# Converts column-oriented dict to DataFrame
columns = {'ids': [1, 2], 'amounts': [100, 200]}
optimized_data = validate_and_prepare_data(columns)
# Returns: pandas DataFrame
```

## Integration with DataProfiler

### Safe Profile Creation
```python
service = DataProfilerService()

if service.is_available():
    # DataProfiler is installed and available
    profile = service.create_profile(financial_data)
    
    if profile:
        print("Profile summary:", profile['summary'])
        print("Column profiles:", profile['column_profiles'])
        print("Data types:", profile['data_types'])
        print("Null analysis:", profile['null_analysis'])
        print("Sensitive data:", profile['sensitive_data'])
else:
    print("DataProfiler not available - install with: pip install dataprofiler")
```

### Configuration Options
```python
# Disable sensitive data detection for performance
service = DataProfilerService(enable_sensitive_data_detection=False)

# Custom DataProfiler options
profile = service.create_profile(
    data,
    samples_per_update=1000,  # Process in batches
    min_true_samples=10      # Minimum samples for statistics
)
```

## Installation

Add to your requirements:
```
dataprofiler>=0.11.0  # Data profiling and sensitive data detection
```

Install with pip:
```bash
pip install dataprofiler
```

## Best Practices

### 1. Always Validate Before Profiling
```python
# Good
try:
    validate_profile_data(data)
    profile = service.create_profile(data)
except ProfileDataError as e:
    logger.error(f"Data validation failed: {e}")
    return None

# Bad
profile = service.create_profile(data)  # May fail with unclear errors
```

### 2. Use Data Preparation for Optimal Performance
```python
# Good - converts to optimal format
prepared_data = validate_and_prepare_data(list_of_records)
profile = service.create_profile(prepared_data)

# Acceptable - but may be less efficient
profile = service.create_profile(list_of_records)
```

### 3. Handle Missing DataProfiler Gracefully
```python
service = DataProfilerService()

if not service.is_available():
    logger.warning("DataProfiler not available, using limited analysis")
    # Fall back to basic analysis
    analysis = service.analyze_financial_data(data)
    # Still provides financial patterns and data quality analysis
```

### 4. Enable Sensitive Data Detection for Financial Data
```python
# For financial applications
service = DataProfilerService(enable_sensitive_data_detection=True)

# Check findings
sensitive_findings = analysis['sensitive_data_detected']
for finding in sensitive_findings:
    if finding['pattern_type'] == 'potential_ssn':
        logger.warning(f"SSN detected in column: {finding['column']}")
```

### 5. Monitor Data Quality
```python
quality = analysis['data_quality']

if quality['missing_data_ratio'] > 0.1:
    logger.warning(f"High missing data ratio: {quality['missing_data_ratio']:.1%}")

if quality['outlier_candidates']:
    logger.info(f"Outliers detected in: {[o['column'] for o in quality['outlier_candidates']]}")
```

## Performance Considerations

### Large Datasets
- DataFrames with >1M rows or >1000 columns generate warnings
- Consider sampling large datasets before profiling
- Use `samples_per_update` parameter for batch processing

### Memory Usage
- Validation creates minimal memory overhead
- Data preparation may create DataFrame copies
- DataProfiler itself can be memory-intensive for large datasets

### Caching
- Consider caching profile results for static datasets
- Validation is fast and doesn't need caching

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'dataprofiler'**
   ```bash
   pip install dataprofiler
   ```

2. **ProfileDataError: DataFrame cannot be empty**
   - Check that your data actually contains records
   - Verify data loading/filtering logic

3. **ProfileDataError: Inconsistent schema**
   - Ensure all records in list have same keys
   - Check for typos in field names

4. **Memory errors with large datasets**
   - Sample your data before profiling
   - Use DataProfiler's sampling options

### Debug Mode

Enable detailed logging:
```python
import logging
logging.getLogger('personal_finance.data_profiler').setLevel(logging.DEBUG)
```

This provides detailed information about:
- Validation steps and decisions
- Data conversion processes
- DataProfiler integration status
- Performance warnings

## Examples

See `examples/data_profiler_usage.py` for comprehensive usage examples including:
- Basic validation scenarios
- Financial data analysis workflows
- Error handling patterns
- Real-world integration examples