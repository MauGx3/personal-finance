# Enhanced Data Analysis Capabilities

This document describes the enhanced data analysis capabilities implemented according to the S.C.A.F.F. structure requirements for the personal finance platform.

## Overview

The platform has been enhanced with modern data analysis libraries and capabilities that provide high-performance data processing, advanced analytics, and comprehensive data quality management.

## Key Libraries Integrated

### Core Data Processing
- **Polars**: High-performance DataFrame library with lazy evaluation
- **pyjanitor**: Data cleaning and tidying for better data quality
- **bt**: Flexible backtesting framework for quantitative trading strategies

### Enhanced Finance Libraries
- **pandas-market-calendars**: Market calendar support for accurate trading day calculations
- **FinanceDatabase**: Access to 300,000+ symbols across all asset classes
- **FinanceToolkit**: 150+ financial ratios and performance measurements

## New Modules

### 1. Polars Integration (`personal_finance.data_sources.polars_integration`)

High-performance data processing with lazy evaluation and optimized queries.

#### Key Features
- Efficient DataFrame operations with automatic library fallback
- Technical indicator calculations (RSI, MACD, Bollinger Bands)
- Portfolio metrics calculation with aggregations
- Moving averages computation

#### Usage Example
```python
from personal_finance.data_sources.polars_integration import polars_processor

# Create DataFrame from price data
price_data = [
    {'symbol': 'AAPL', 'date': '2024-01-01', 'close_price': 180.0, 'volume': 1000000},
    {'symbol': 'AAPL', 'date': '2024-01-02', 'close_price': 182.0, 'volume': 1200000},
]

df = polars_processor.create_price_dataframe(price_data)

# Calculate moving averages
df_with_ma = polars_processor.calculate_moving_averages(df, windows=[20, 50])

# Calculate technical indicators
df_with_indicators = polars_processor.calculate_technical_indicators(df_with_ma)

# Calculate portfolio metrics
portfolio_data = [
    {'symbol': 'AAPL', 'quantity': 100, 'cost_basis': 15000, 'current_value': 18000},
    {'symbol': 'GOOGL', 'quantity': 50, 'cost_basis': 25000, 'current_value': 27000},
]

metrics = polars_processor.calculate_portfolio_metrics(portfolio_data)
print(f"Total return: ${metrics['total_return']:,.2f}")
print(f"Return percentage: {metrics['return_percentage']:.2f}%")
```

### 2. Data Profiling (`personal_finance.data_sources.data_profiling`)

Comprehensive data analysis including sensitive data detection and quality assessment.

#### Key Features
- Automatic schema detection and statistical profiling
- Sensitive data (PII/NPI) detection for compliance
- Financial pattern analysis
- Data quality issue identification
- Comprehensive profiling reports with recommendations

#### Usage Example
```python
from personal_finance.data_sources.data_profiling import financial_profiler
import pandas as pd

# Profile portfolio data
portfolio_data = [
    {'symbol': 'AAPL', 'price': 180.0, 'ssn': '123-45-6789'},  # Contains PII
    {'symbol': 'GOOGL', 'price': 2800.0, 'email': 'user@example.com'},
]

df = pd.DataFrame(portfolio_data)
profile_results = financial_profiler.profile_financial_data(df)

# Check for sensitive data alerts
if profile_results['sensitive_data_alerts']:
    print("⚠️ Sensitive data detected!")
    for alert in profile_results['sensitive_data_alerts']:
        print(f"  - {alert['column']}: {alert['data_label']} ({alert['severity']})")

# Validate financial data types
validation = financial_profiler.validate_financial_data_types({
    'price': 150.50,  # float - will trigger precision warning
    'amount': Decimal('1000.00'),  # Decimal - good practice
})

if not validation['valid']:
    print("Data type issues found:")
    for issue in validation['issues']:
        print(f"  - {issue['field']}: {issue['recommendation']}")
```

### 3. Data Cleaning (`personal_finance.data_sources.data_cleaning`)

Advanced data cleaning and tidying using pyjanitor and custom financial data methods.

#### Key Features
- Column name standardization (snake_case)
- Currency symbol removal and handling
- Financial data type conversions with Decimal precision
- Date format standardization
- Empty row/column removal
- Financial value cleaning with proper precision

#### Usage Example
```python
from personal_finance.data_sources.data_cleaning import financial_cleaner

# Clean messy financial data
messy_data = [
    {
        'Stock Symbol': 'AAPL',
        'Purchase Price': '$150.50',
        'Current Price': '$180,25',
        'Purchase Date': '2024-01-01',
        'Total Value': '($18,025.00)',  # Negative in parentheses
    }
]

cleaned_data = financial_cleaner.clean_portfolio_data(messy_data)

# Result will have:
# - Standardized column names (stock_symbol, purchase_price, etc.)
# - Currency symbols removed
# - Proper Decimal types for financial values
# - Standardized date formats
# - Negative values properly handled

# Clean DataFrames
import pandas as pd
df = pd.DataFrame(messy_data)
cleaned_df = financial_cleaner.clean_financial_dataframe(df)

# Generate cleaning report
report = financial_cleaner.generate_cleaning_report(df, cleaned_df)
print(f"Cleaned {report['cleaning_summary']['rows_removed']} problematic rows")
```

## Management Commands

### Demo Command: `demo_polars_analysis`

Comprehensive demonstration of enhanced data analysis capabilities.

```bash
# Run all demos
python manage.py demo_polars_analysis

# Run specific demo types
python manage.py demo_polars_analysis --demo-type portfolio
python manage.py demo_polars_analysis --demo-type technical
python manage.py demo_polars_analysis --demo-type performance

# Customize symbols and time period
python manage.py demo_polars_analysis --symbols AAPL GOOGL MSFT TSLA --days 90

# Dry run to see what would be analyzed
python manage.py demo_polars_analysis --dry-run
```

This command demonstrates:
- Portfolio analysis with modern data processing
- Technical indicator calculations
- Performance benchmarking between libraries
- Available capabilities assessment

## Performance Benefits

### Polars vs Pandas Performance
- **Lazy Evaluation**: Polars optimizes query plans before execution
- **Memory Efficiency**: Better memory usage for large datasets
- **Parallel Processing**: Automatic parallelization of operations
- **Type Safety**: Strong typing reduces runtime errors

### Example Performance Comparison
```python
# The demo command includes performance benchmarking
python manage.py demo_polars_analysis --demo-type performance

# Typical results show Polars 2-10x faster for large datasets
# Memory usage is often 50-70% lower than equivalent Pandas operations
```

## Integration with Existing Code

### Graceful Fallbacks
All new modules include graceful fallbacks:
- If Polars is not available, operations fall back to Pandas
- If DataProfiler is not available, basic profiling is still provided
- Missing optional dependencies don't break existing functionality

### Backward Compatibility
- Existing Django models and APIs remain unchanged
- New capabilities are additive, not replacement
- Can be adopted incrementally as needed

## Testing

### Comprehensive Test Suite
The new functionality includes comprehensive tests:

```bash
# Run enhanced data analysis tests
pytest tests/test_enhanced_data_analysis.py -v

# Run specific test categories
pytest tests/test_enhanced_data_analysis.py::TestDataAnalysisIntegration -v
pytest tests/test_enhanced_data_analysis.py::TestEndToEndDataAnalysisWorkflow -v

# Run performance comparison tests
pytest tests/test_enhanced_data_analysis.py -k "performance" -v
```

### Test Coverage
- Unit tests for each new module
- Integration tests for complete workflows
- Performance comparison tests
- Graceful degradation tests
- Error handling and edge cases

## Best Practices

### Financial Data Precision
```python
# ✅ Good: Use Decimal for financial calculations
from decimal import Decimal
price = Decimal('150.50')
quantity = Decimal('100')
total = price * quantity

# ❌ Avoid: Float precision issues
price = 150.50  # Can lead to precision errors
```

### Data Cleaning Workflow
```python
# 1. Clean raw data first
cleaned_data = financial_cleaner.clean_portfolio_data(raw_data)

# 2. Profile for quality assessment
profile = financial_profiler.profile_portfolio_data(cleaned_data)

# 3. Process with high-performance tools
df = polars_processor.create_price_dataframe(cleaned_data)
metrics = polars_processor.calculate_portfolio_metrics(cleaned_data)
```

### Memory Management for Large Datasets
```python
# Use Polars lazy evaluation for large datasets
lazy_df = pl.scan_csv("large_financial_data.csv")
result = lazy_df.filter(pl.col("volume") > 1000000).group_by("symbol").agg([
    pl.col("close_price").mean().alias("avg_price"),
    pl.col("volume").sum().alias("total_volume")
]).collect()  # Only executes when .collect() is called
```

## Future Extensions

The enhanced data analysis framework provides a foundation for:

### Additional Finance Libraries
- Integration with remaining S.C.A.F.F. libraries as they become available
- Custom financial indicators and metrics
- Advanced portfolio optimization algorithms

### Real-time Processing
- Streaming data analysis with Polars
- Real-time technical indicator updates
- Live portfolio monitoring

### Machine Learning Integration
- Feature engineering with cleaned financial data
- Predictive modeling for portfolio optimization
- Risk assessment algorithms

## Troubleshooting

### Common Issues

#### Library Not Available
```python
# Check library availability
from personal_finance.data_sources.polars_integration import polars_processor
print(f"Polars available: {polars_processor.polars_available}")
print(f"Pandas available: {polars_processor.pandas_available}")
```

#### Performance Issues
```python
# For large datasets, use Polars lazy evaluation
# Instead of:
df = polars_processor.create_price_dataframe(large_data)  # Loads all into memory

# Use:
lazy_df = pl.DataFrame(large_data).lazy()
result = lazy_df.filter(...).select(...).collect()  # Optimized execution
```

#### Data Type Issues
```python
# Validate financial data types
validation = financial_profiler.validate_financial_data_types(data)
if not validation['valid']:
    for issue in validation['issues']:
        print(f"Fix needed: {issue['recommendation']}")
```

For additional support and examples, see the comprehensive test suite in `tests/test_enhanced_data_analysis.py`.