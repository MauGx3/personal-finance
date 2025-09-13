"""
Example usage of the DataProfiler validation and service functionality.

This module demonstrates how to use the new DataProfiler integration 
with validation to analyze financial data safely.
"""

import pandas as pd
import numpy as np
from personal_finance.data_profiler import (
    validate_profile_data, 
    validate_and_prepare_data,
    DataProfilerService,
    ProfileDataError
)


def example_basic_validation():
    """Demonstrate basic data validation for DataProfiler compatibility."""
    print("=== Basic Data Validation Examples ===\n")
    
    # Example 1: Valid DataFrame
    print("1. Validating a financial DataFrame:")
    financial_df = pd.DataFrame({
        'transaction_id': ['TXN001', 'TXN002', 'TXN003'],
        'amount': [100.50, 250.75, 75.25],
        'transaction_type': ['debit', 'credit', 'debit'],
        'account_id': ['ACC001', 'ACC002', 'ACC001'],
    })
    
    try:
        is_valid = validate_profile_data(financial_df)
        print(f"✓ DataFrame validation: {is_valid}")
        print(f"  Shape: {financial_df.shape}")
        print(f"  Columns: {list(financial_df.columns)}")
    except ProfileDataError as e:
        print(f"✗ Validation failed: {e}")
    
    print()
    
    # Example 2: List of dictionaries (records format)
    print("2. Validating portfolio data as list of records:")
    portfolio_data = [
        {
            'symbol': 'AAPL',
            'quantity': 100,
            'purchase_price': 150.25,
            'current_price': 175.50
        },
        {
            'symbol': 'GOOGL', 
            'quantity': 50,
            'purchase_price': 2800.75,
            'current_price': 2950.25
        }
    ]
    
    try:
        is_valid = validate_profile_data(portfolio_data)
        print(f"✓ Portfolio data validation: {is_valid}")
        print(f"  Records count: {len(portfolio_data)}")
        print(f"  Fields: {list(portfolio_data[0].keys()) if portfolio_data else []}")
    except ProfileDataError as e:
        print(f"✗ Validation failed: {e}")
    
    print()
    
    # Example 3: Invalid data (None)
    print("3. Validating invalid data (None):")
    try:
        validate_profile_data(None)
        print("✗ This should not print")
    except ProfileDataError as e:
        print(f"✓ Correctly caught error: {e}")
    
    print()


def example_data_preparation():
    """Demonstrate data preparation for optimal DataProfiler usage."""
    print("=== Data Preparation Examples ===\n")
    
    # Example 1: Converting list of dicts to DataFrame
    print("1. Converting list of records to DataFrame:")
    transaction_records = [
        {'id': 'T001', 'amount': 100.0, 'type': 'debit'},
        {'id': 'T002', 'amount': 250.0, 'type': 'credit'},
        {'id': 'T003', 'amount': 75.0, 'type': 'debit'}
    ]
    
    prepared_data = validate_and_prepare_data(transaction_records)
    print(f"Original type: {type(transaction_records)}")
    print(f"Prepared type: {type(prepared_data)}")
    if isinstance(prepared_data, pd.DataFrame):
        print(f"DataFrame shape: {prepared_data.shape}")
        print(f"Columns: {list(prepared_data.columns)}")
    
    print()
    
    # Example 2: Column-oriented dictionary to DataFrame
    print("2. Converting column-oriented dict to DataFrame:")
    price_data = {
        'dates': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'prices': [100.0, 102.5, 98.5],
        'volumes': [1000000, 1200000, 950000]
    }
    
    prepared_data = validate_and_prepare_data(price_data)
    print(f"Original type: {type(price_data)}")
    print(f"Prepared type: {type(prepared_data)}")
    if isinstance(prepared_data, pd.DataFrame):
        print(f"DataFrame shape: {prepared_data.shape}")
        print(f"Columns: {list(prepared_data.columns)}")
    
    print()


def example_service_usage():
    """Demonstrate DataProfiler service usage."""
    print("=== DataProfiler Service Examples ===\n")
    
    # Initialize the service
    service = DataProfilerService(enable_sensitive_data_detection=True)
    print(f"DataProfiler available: {service.is_available()}")
    
    # Create sample financial data
    financial_data = pd.DataFrame({
        'transaction_id': ['TXN001', 'TXN002', 'TXN003', 'TXN004'],
        'account_number': ['1234567890', '0987654321', '1234567890', '5555555555'],
        'amount': [1500.75, 250.00, 75.50, 10000.00],  # Last amount is suspicious
        'transaction_type': ['credit', 'debit', 'debit', 'credit'],
        'transaction_date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18'],
        'customer_ssn': ['123-45-6789', '987-65-4321', '555-44-3333', '111-22-3333']
    })
    
    print("1. Analyzing financial data:")
    try:
        analysis_result = service.analyze_financial_data(financial_data)
        
        print("✓ Analysis completed successfully")
        print(f"  Components analyzed: {list(analysis_result.keys())}")
        
        # Show financial patterns
        patterns = analysis_result['financial_patterns']
        print(f"  Amount columns detected: {patterns['potential_amount_columns']}")
        print(f"  Date columns detected: {patterns['potential_date_columns']}")
        
        # Show data quality issues
        quality = analysis_result['data_quality']
        print(f"  Missing data ratio: {quality['missing_data_ratio']:.2%}")
        print(f"  Duplicate rows: {quality['duplicate_rows']}")
        print(f"  Outlier candidates: {len(quality['outlier_candidates'])}")
        
        # Show sensitive data findings
        sensitive_data = analysis_result['sensitive_data_detected']
        print(f"  Sensitive data patterns found: {len(sensitive_data)}")
        for finding in sensitive_data:
            print(f"    - Column '{finding['column']}': {finding['pattern_type']}")
        
    except ProfileDataError as e:
        print(f"✗ Analysis failed: {e}")
    
    print()
    
    # Example with basic profiling (if DataProfiler is available)
    if service.is_available():
        print("2. Creating basic profile (DataProfiler available):")
        try:
            simple_data = pd.DataFrame({
                'amounts': [100, 200, 300, 400, 500],
                'categories': ['food', 'transport', 'entertainment', 'food', 'transport']
            })
            
            profile = service.create_profile(simple_data)
            if profile:
                print("✓ Profile created successfully")
                print(f"  Summary: {profile.get('summary', {})}")
                print(f"  Data types: {profile.get('data_types', {})}")
            else:
                print("✗ Profile creation returned None")
                
        except ProfileDataError as e:
            print(f"✗ Profile creation failed: {e}")
    else:
        print("2. DataProfiler not available - install with: pip install dataprofiler")
    
    print()


def example_error_handling():
    """Demonstrate error handling scenarios."""
    print("=== Error Handling Examples ===\n")
    
    # Example 1: Empty DataFrame
    print("1. Handling empty DataFrame:")
    empty_df = pd.DataFrame()
    try:
        validate_profile_data(empty_df)
        print("✗ This should not print")
    except ProfileDataError as e:
        print(f"✓ Correctly handled error: {e}")
    
    print()
    
    # Example 2: Inconsistent record structure
    print("2. Handling inconsistent records:")
    inconsistent_records = [
        {'name': 'John', 'age': 30},
        {'name': 'Jane', 'salary': 50000}  # Different keys
    ]
    try:
        validate_profile_data(inconsistent_records)
        print("✗ This should not print")
    except ProfileDataError as e:
        print(f"✓ Correctly handled error: {e}")
    
    print()
    
    # Example 3: Unsupported data type
    print("3. Handling unsupported data type:")
    try:
        validate_profile_data(set([1, 2, 3]))  # Set is not supported
        print("✗ This should not print")
    except ProfileDataError as e:
        print(f"✓ Correctly handled error: {e}")
    
    print()


def example_financial_scenarios():
    """Demonstrate real-world financial data scenarios."""
    print("=== Real-World Financial Data Scenarios ===\n")
    
    service = DataProfilerService(enable_sensitive_data_detection=True)
    
    # Scenario 1: Portfolio holdings analysis
    print("1. Portfolio holdings analysis:")
    portfolio_df = pd.DataFrame({
        'symbol': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA'],
        'quantity': [100, 50, 75, 25, 30],
        'purchase_price': [150.25, 2800.75, 300.50, 3200.00, 250.75],
        'current_price': [175.50, 2950.25, 325.75, 3150.50, 220.25],
        'sector': ['Technology', 'Technology', 'Technology', 'Consumer Discretionary', 'Consumer Discretionary'],
        'purchase_date': ['2024-01-15', '2024-01-20', '2024-02-01', '2024-02-10', '2024-02-15']
    })
    
    try:
        # Validate and analyze
        validate_profile_data(portfolio_df)
        analysis = service.analyze_financial_data(portfolio_df)
        
        print("✓ Portfolio analysis completed")
        patterns = analysis['financial_patterns']
        print(f"  Price columns: {patterns['potential_amount_columns']}")
        print(f"  Date columns: {patterns['potential_date_columns']}")
        
        quality = analysis['data_quality']
        print(f"  Data quality score: {1 - quality['missing_data_ratio']:.1%}")
        
    except ProfileDataError as e:
        print(f"✗ Portfolio analysis failed: {e}")
    
    print()
    
    # Scenario 2: Transaction history with sensitive data
    print("2. Transaction history with PII detection:")
    transactions_df = pd.DataFrame({
        'transaction_id': [f'TXN{i:04d}' for i in range(1, 101)],
        'account_number': ['1234567890'] * 50 + ['0987654321'] * 50,
        'amount': np.random.uniform(10, 1000, 100).round(2),
        'transaction_type': np.random.choice(['debit', 'credit'], 100),
        'merchant': ['Grocery Store', 'Gas Station', 'Restaurant', 'Online Store'] * 25,
        'customer_id': [f'CUST{i:04d}' for i in range(1, 101)]
    })
    
    try:
        analysis = service.analyze_financial_data(transactions_df)
        
        print("✓ Transaction analysis completed")
        print(f"  Transactions analyzed: {len(transactions_df)}")
        
        sensitive_findings = analysis['sensitive_data_detected']
        print(f"  Sensitive data patterns: {len(sensitive_findings)}")
        for finding in sensitive_findings:
            print(f"    - {finding['column']}: {finding['pattern_type']}")
        
        quality = analysis['data_quality']
        if quality['outlier_candidates']:
            print(f"  Outlier candidates found in: {[o['column'] for o in quality['outlier_candidates']]}")
        
    except ProfileDataError as e:
        print(f"✗ Transaction analysis failed: {e}")
    
    print()


if __name__ == "__main__":
    """Run all examples."""
    print("DataProfiler Validation and Service Examples")
    print("=" * 50)
    print()
    
    example_basic_validation()
    example_data_preparation()
    example_service_usage()
    example_error_handling()
    example_financial_scenarios()
    
    print("=" * 50)
    print("Examples completed!")
    print("\nNext steps:")
    print("1. Install DataProfiler: pip install dataprofiler")
    print("2. Import the validation functions in your code")
    print("3. Always validate data before creating DataProfiler instances")
    print("4. Use the service class for comprehensive financial data analysis")