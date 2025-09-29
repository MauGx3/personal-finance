Data Profiling and Analysis
==========================

Comprehensive data profiling and analysis reference using DataProfiler integration.

.. currentmodule:: personal_finance.data_profiler

.. contents:: Table of Contents
   :local:
   :depth: 3

Module Overview
---------------

The Data Profiler module provides comprehensive data analysis, validation, and sensitive data detection specifically designed for financial applications:

.. toctree::
   :maxdepth: 2

   Services <services/data_profiler>
   Validators <validators/data_profiler>
   Analysis <analysis/data_profiler>
   Integration <integration/data_profiler>

Core Features
~~~~~~~~~~~~~

- **Data Validation**: Comprehensive validation before DataProfiler processing
- **Financial Pattern Detection**: Identification of financial data patterns and anomalies
- **Sensitive Data Detection**: Financial-specific PII and sensitive data identification
- **Data Quality Analysis**: Comprehensive analysis of data quality issues
- **Safe Integration**: Graceful handling when DataProfiler is unavailable
- **Performance Optimization**: Intelligent data preparation for optimal processing

Data Validation Framework
-------------------------

ProfileDataError Exception
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: personal_finance.data_profiler.exceptions.ProfileDataError
   :members:
   :undoc-members:
   :show-inheritance:

All data validation failures raise this specific exception for clear error handling:

.. code-block:: python

   from personal_finance.data_profiler import validate_profile_data, ProfileDataError

   try:
       validate_profile_data(financial_data)
       print(\"✅ Data is valid for profiling\")
   except ProfileDataError as e:
       print(f\"❌ Validation failed: {e}\")
       # Handle validation error appropriately

Core Validation Function
~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: personal_finance.data_profiler.validators.validate_profile_data

Comprehensive data validation supporting all DataProfiler-compatible formats:

.. code-block:: python

   import pandas as pd
   import numpy as np
   from personal_finance.data_profiler import validate_profile_data

   # Pandas DataFrame validation
   financial_df = pd.DataFrame({
       'transaction_id': ['TXN001', 'TXN002', 'TXN003'],
       'amount': [100.50, -250.75, 1500.00],
       'account_id': ['ACC001', 'ACC002', 'ACC001'],
       'date': ['2024-01-15', '2024-01-16', '2024-01-17']
   })
   validate_profile_data(financial_df)  # ✅ Valid

   # Pandas Series validation
   price_series = pd.Series([150.25, 152.80, 148.90], name='stock_prices')
   validate_profile_data(price_series)  # ✅ Valid

   # NumPy array validation
   price_matrix = np.array([[100, 102], [98, 105], [103, 99]])
   validate_profile_data(price_matrix)  # ✅ Valid

   # List of records validation
   portfolio_records = [
       {'symbol': 'AAPL', 'quantity': 100, 'price': 150.25, 'account': 'IRA'},
       {'symbol': 'GOOGL', 'quantity': 50, 'price': 2800.75, 'account': 'Taxable'},
       {'symbol': 'MSFT', 'quantity': 75, 'price': 420.30, 'account': 'IRA'}
   ]
   validate_profile_data(portfolio_records)  # ✅ Valid

   # Column-oriented dictionary validation
   market_data = {
       'symbols': ['AAPL', 'GOOGL', 'MSFT'],
       'prices': [150.25, 2800.75, 420.30],
       'volumes': [1000000, 800000, 1200000],
       'market_caps': [2.8e12, 1.9e12, 3.1e12]
   }
   validate_profile_data(market_data)  # ✅ Valid

   # File path validation
   validate_profile_data('portfolio_data.csv')  # ✅ Valid
   validate_profile_data('/data/financial_records.xlsx')  # ✅ Valid

Supported Data Formats
~~~~~~~~~~~~~~~~~~~~~~

**DataFrame Validation Rules:**
   - Must not be empty (at least 1 row and 1 column)
   - Column names must be strings, integers, or floats
   - No empty string column names
   - Warnings for very large DataFrames (>1M rows or >1000 columns)

**Series Validation Rules:**
   - Must not be empty
   - Series name (if provided) must be string, integer, or float

**NumPy Array Rules:**
   - Must not be empty
   - Maximum 2 dimensions (DataProfiler limitation)
   - Warnings for object arrays with multiple dimensions

**List Validation Rules:**
   - Must not be empty
   - For list of dictionaries: consistent schema across all records
   - For simple lists: mixed types allowed with warnings for excessive diversity

**Dictionary Validation Rules:**
   - Must not be empty
   - For column-oriented data: all arrays/lists must have equal length
   - For record data: validates as single record structure

**File Path Rules:**
   - Must not be empty or whitespace-only
   - Supported extensions: `.csv`, `.json`, `.parquet`, `.xlsx`, `.xls`, `.txt`
   - Warnings for unsupported extensions

Data Preparation and Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: personal_finance.data_profiler.validators.validate_and_prepare_data

Intelligent data preparation for optimal DataProfiler performance:

.. code-block:: python

   from personal_finance.data_profiler import validate_and_prepare_data

   # Convert list of records to optimized DataFrame
   transaction_records = [
       {'date': '2024-01-15', 'symbol': 'AAPL', 'quantity': 100, 'price': 150.25},
       {'date': '2024-01-16', 'symbol': 'GOOGL', 'quantity': 50, 'price': 2800.75},
       {'date': '2024-01-17', 'symbol': 'MSFT', 'quantity': 75, 'price': 420.30}
   ]

   # Optimizes to DataFrame for better DataProfiler performance
   optimized_data = validate_and_prepare_data(transaction_records)
   print(type(optimized_data))  # <class 'pandas.core.frame.DataFrame'>

   # Convert column-oriented dictionary to DataFrame
   portfolio_columns = {
       'symbols': ['AAPL', 'GOOGL', 'MSFT'],
       'quantities': [100, 50, 75],
       'prices': [150.25, 2800.75, 420.30],
       'values': [15025.00, 140037.50, 31522.50]
   }

   optimized_portfolio = validate_and_prepare_data(portfolio_columns)
   print(optimized_portfolio.shape)  # (3, 4)
   print(optimized_portfolio.columns.tolist())  # ['symbols', 'quantities', 'prices', 'values']

DataProfiler Service Integration
-------------------------------

Core Service Class
~~~~~~~~~~~~~~~~~~

.. autoclass:: personal_finance.data_profiler.services.DataProfilerService
   :members:
   :undoc-members:
   :show-inheritance:

The main service class providing DataProfiler integration with financial data specialization:

.. code-block:: python

   from personal_finance.data_profiler import DataProfilerService

   # Initialize service with sensitive data detection enabled
   service = DataProfilerService(enable_sensitive_data_detection=True)

   # Check if DataProfiler is available in the environment
   if service.is_available():
       print(\"✅ DataProfiler is available and ready\")
   else:
       print(\"❌ DataProfiler not available - install with: pip install dataprofiler\")

   # Analyze financial data comprehensively
   financial_data = pd.DataFrame({
       'account_number': ['1234567890', '9876543210', '5555666677'],
       'transaction_amount': [1500.50, -250.75, 3200.00],
       'transaction_date': ['2024-01-15', '2024-01-16', '2024-01-17'],
       'description': ['Stock Purchase - AAPL', 'Dividend - GOOGL', 'Stock Sale - MSFT']
   })

   analysis_result = service.analyze_financial_data(financial_data)

   # Access comprehensive analysis results
   print(\"Financial Patterns:\", analysis_result['financial_patterns'])
   print(\"Data Quality Metrics:\", analysis_result['data_quality'])
   print(\"Sensitive Data Detected:\", analysis_result['sensitive_data_detected'])

Financial Data Analysis
~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: personal_finance.data_profiler.services.DataProfilerService.analyze_financial_data

Comprehensive analysis specifically designed for financial datasets:

.. code-block:: python

   # Analyze portfolio data
   portfolio_df = pd.DataFrame({
       'symbol': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA'],
       'quantity': [100, 25, 150, 75, 50],
       'avg_cost': [145.50, 2750.25, 380.80, 3200.75, 850.30],
       'current_price': [150.25, 2800.75, 420.30, 3150.50, 875.60],
       'account_type': ['IRA', 'Taxable', 'IRA', 'Roth IRA', 'Taxable'],
       'purchase_date': ['2023-01-15', '2023-03-20', '2023-06-10', '2023-08-05', '2023-11-12']
   })

   analysis = service.analyze_financial_data(portfolio_df)

   # Financial pattern detection
   patterns = analysis['financial_patterns']
   print(f\"Currency columns detected: {patterns['potential_currency_columns']}\")
   print(f\"Date columns detected: {patterns['potential_date_columns']}\")
   print(f\"Amount columns detected: {patterns['potential_amount_columns']}\")

   # Data quality assessment
   quality = analysis['data_quality']
   print(f\"Missing data ratio: {quality['missing_data_ratio']:.2%}\")
   print(f\"Duplicate rows: {quality['duplicate_rows']}\")
   print(f\"Outlier candidates: {[col['column'] for col in quality['outlier_candidates']]}\")

   # Sensitive data detection
   sensitive = analysis['sensitive_data_detected']
   for finding in sensitive:
       print(f\"⚠️  {finding['pattern_type']} detected in column '{finding['column']}'\"
             f\" (confidence: {finding['confidence']})\")

DataProfiler Profile Creation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: personal_finance.data_profiler.services.DataProfilerService.create_profile

Create comprehensive DataProfiler profiles with financial data optimizations:

.. code-block:: python

   # Create detailed profile with custom options
   profile_result = service.create_profile(
       financial_data,
       samples_per_update=1000,  # Process in batches for large datasets
       min_true_samples=10,      # Minimum samples required for statistics
       max_sample_size=50000     # Limit sample size for performance
   )

   if profile_result:
       print(\"📊 Profile Summary:\")
       summary = profile_result['summary']
       print(f\"  Dataset shape: {summary['shape']}\")
       print(f\"  Total memory usage: {summary['memory_size']}\")
       print(f\"  Data types: {summary['data_types']}\")

       print(\"\\n📈 Column Profiles:\")
       for col_name, col_profile in profile_result['column_profiles'].items():
           print(f\"  {col_name}:\")
           print(f\"    Type: {col_profile['data_type']}\")
           print(f\"    Null count: {col_profile['null_count']}\")
           if 'statistics' in col_profile:
               stats = col_profile['statistics']
               if 'mean' in stats:
                   print(f\"    Mean: {stats['mean']:.2f}\")
               if 'std' in stats:
                   print(f\"    Std Dev: {stats['std']:.2f}\")

       print(\"\\n🔍 Sensitive Data Analysis:\")
       if profile_result['sensitive_data']:
           for detection in profile_result['sensitive_data']:
               print(f\"  {detection['data_type']} in column '{detection['column']}'\"
                     f\" (confidence: {detection['confidence']:.1%})\")
       else:
           print(\"  No sensitive data patterns detected\")

Pattern Detection
-----------------

Financial Pattern Recognition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The system includes sophisticated pattern recognition for financial data:

.. code-block:: python

   from personal_finance.data_profiler.analysis import FinancialPatternDetector

   detector = FinancialPatternDetector()

   # Detect currency/amount patterns
   currency_columns = detector.detect_currency_columns(financial_df)
   print(f\"Currency columns: {currency_columns}\")

   # Detect date patterns in financial context
   date_columns = detector.detect_financial_date_columns(financial_df)
   print(f\"Financial date columns: {date_columns}\")

   # Detect account number patterns
   account_columns = detector.detect_account_number_patterns(financial_df)
   for col, pattern_info in account_columns.items():
       print(f\"Account pattern in '{col}': {pattern_info['pattern_type']}\"
             f\" (confidence: {pattern_info['confidence']:.1%})\")

   # Detect suspicious patterns
   suspicious = detector.detect_suspicious_patterns(financial_df)
   for pattern in suspicious:
       print(f\"⚠️  Suspicious pattern: {pattern['description']}\"
             f\" in column '{pattern['column']}'\"
             f\" (severity: {pattern['severity']})\")

Data Quality Analysis
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: personal_finance.data_profiler.analysis.DataQualityAnalyzer
   :members:
   :undoc-members:

Comprehensive data quality assessment:

.. code-block:: python

   from personal_finance.data_profiler.analysis import DataQualityAnalyzer

   quality_analyzer = DataQualityAnalyzer()

   # Comprehensive quality assessment
   quality_report = quality_analyzer.analyze_data_quality(financial_df)

   print(\"📋 Data Quality Report:\")
   print(f\"Overall quality score: {quality_report['overall_score']}/100\")

   # Missing data analysis
   missing = quality_report['missing_data_analysis']
   print(f\"\\n🔍 Missing Data Analysis:\")
   print(f\"  Total missing values: {missing['total_missing']}\")
   print(f\"  Missing data ratio: {missing['missing_ratio']:.2%}\")

   if missing['columns_with_missing']:
       print(f\"  Columns with missing data:\")
       for col, ratio in missing['columns_with_missing'].items():
           print(f\"    {col}: {ratio:.1%} missing\")

   # Duplicate analysis
   duplicates = quality_report['duplicate_analysis']
   if duplicates['duplicate_rows'] > 0:
       print(f\"\\n📄 Duplicate Analysis:\")
       print(f\"  Duplicate rows: {duplicates['duplicate_rows']}\")
       print(f\"  Duplicate ratio: {duplicates['duplicate_ratio']:.2%}\")

   # Outlier detection
   outliers = quality_report['outlier_analysis']
   if outliers['outlier_candidates']:
       print(f\"\\n📊 Outlier Analysis:\")
       for outlier in outliers['outlier_candidates']:
           print(f\"  Column '{outlier['column']}': {outlier['outlier_count']} potential outliers\"
                 f\" (method: {outlier['detection_method']})\")

   # Data consistency
   consistency = quality_report['consistency_analysis']
   if consistency['inconsistencies']:
       print(f\"\\n⚠️  Consistency Issues:\")
       for issue in consistency['inconsistencies']:
           print(f\"  {issue['type']}: {issue['description']}\")

Sensitive Data Detection
-----------------------

Financial PII Detection
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: personal_finance.data_profiler.security.SensitiveDataDetector
   :members:
   :undoc-members:

Specialized detection of financial personally identifiable information:

.. code-block:: python

   from personal_finance.data_profiler.security import SensitiveDataDetector

   # Initialize detector with financial patterns
   detector = SensitiveDataDetector(enable_financial_patterns=True)

   # Sample financial data with potential PII
   sensitive_df = pd.DataFrame({
       'customer_id': ['CUST001', 'CUST002', 'CUST003'],
       'account_number': ['1234567890123456', '9876543210987654', '5555444433332222'],
       'ssn': ['123-45-6789', '987-65-4321', '555-44-3333'],
       'credit_card': ['4111-1111-1111-1111', '5555-5555-5555-4444', '3782-822463-10005'],
       'routing_number': ['121000248', '011401533', '324377516'],
       'transaction_amount': [1500.50, 2750.25, 950.75]
   })

   # Detect sensitive patterns
   sensitive_findings = detector.detect_sensitive_data(sensitive_df)

   print(\"🚨 Sensitive Data Detection Results:\")
   for finding in sensitive_findings:
       print(f\"\\n Pattern: {finding['pattern_type']}\")
       print(f\" Column: {finding['column']}\")
       print(f\" Confidence: {finding['confidence']:.1%}\")
       print(f\" Samples detected: {finding['sample_count']}\")
       print(f\" Recommendation: {finding['recommendation']}\")

       if finding['examples']:
           print(f\" Example patterns: {finding['examples'][:3]}...\")

Account Number Detection
~~~~~~~~~~~~~~~~~~~~~~~

Specialized detection for financial account numbers:

.. code-block:: python

   # Detect various account number formats
   account_patterns = detector.detect_account_numbers(sensitive_df['account_number'])

   for detection in account_patterns:
       print(f\"Account type: {detection['account_type']}\")
       print(f\"Pattern: {detection['pattern']}\")
       print(f\"Confidence: {detection['confidence']:.1%}\")
       print(f\"Length range: {detection['length_range']}\")

Credit Card Detection
~~~~~~~~~~~~~~~~~~~~

Advanced credit card number detection with validation:

.. code-block:: python

   # Detect and validate credit card numbers
   credit_card_findings = detector.detect_credit_cards(sensitive_df['credit_card'])

   for finding in credit_card_findings:
       print(f\"Card type: {finding['card_type']} ({finding['issuer']})\")
       print(f\"Valid Luhn: {finding['luhn_valid']}\")
       print(f\"Masked number: {finding['masked_number']}\")
       print(f\"Confidence: {finding['confidence']:.1%}\")

Performance Optimization
-----------------------

Large Dataset Handling
~~~~~~~~~~~~~~~~~~~~~~

Optimizations for processing large financial datasets:

.. code-block:: python

   from personal_finance.data_profiler.performance import LargeDatasetHandler

   # Initialize handler for big data processing
   handler = LargeDatasetHandler(
       max_sample_size=100000,  # Limit sample size
       chunk_size=10000,        # Process in chunks
       enable_parallel=True     # Use multiprocessing
   )

   # Process large dataset efficiently
   large_portfolio = pd.read_csv('large_portfolio.csv')  # Assume 1M+ rows

   print(f\"Original dataset: {large_portfolio.shape}\")

   # Smart sampling for profiling
   sample_data = handler.create_representative_sample(large_portfolio)
   print(f\"Representative sample: {sample_data.shape}\")

   # Process with optimizations
   analysis = service.analyze_financial_data(
       sample_data,
       use_sampling=True,
       parallel_processing=True
   )

   print(\"✅ Large dataset analysis completed efficiently\")

Memory Management
~~~~~~~~~~~~~~~~~

Intelligent memory management for resource optimization:

.. code-block:: python

   from personal_finance.data_profiler.performance import MemoryOptimizer

   optimizer = MemoryOptimizer()

   # Monitor memory usage during profiling
   with optimizer.memory_monitor() as monitor:
       profile = service.create_profile(large_financial_dataset)

   print(f\"Peak memory usage: {monitor.peak_memory_mb:.1f} MB\")
   print(f\"Memory efficiency score: {monitor.efficiency_score}/100\")

   # Optimize DataFrame memory usage
   optimized_df = optimizer.optimize_dataframe_memory(financial_df)

   original_size = financial_df.memory_usage(deep=True).sum()
   optimized_size = optimized_df.memory_usage(deep=True).sum()
   savings = (1 - optimized_size / original_size) * 100

   print(f\"Memory savings: {savings:.1f}%\")

Batch Processing
~~~~~~~~~~~~~~~

Process large datasets in manageable batches:

.. code-block:: python

   from personal_finance.data_profiler.batch import BatchProcessor

   processor = BatchProcessor(batch_size=5000)

   # Process large CSV file in batches
   batch_results = []
   for batch_df in processor.process_csv_in_batches('huge_transactions.csv'):
       batch_analysis = service.analyze_financial_data(batch_df)
       batch_results.append(batch_analysis)

   # Combine batch results
   combined_analysis = processor.combine_batch_results(batch_results)

   print(f\"Processed {len(batch_results)} batches\")
   print(f\"Combined results: {combined_analysis['summary']}\")

Integration Examples
-------------------

Django Model Integration
~~~~~~~~~~~~~~~~~~~~~~~

Integrate with Django models for automatic data profiling:

.. code-block:: python

   from django.db import models
   from personal_finance.data_profiler import DataProfilerService

   class PortfolioDataProfile(models.Model):
       \"\"\"Store data profiling results for portfolios.\"\"\"

       portfolio = models.ForeignKey('portfolio.Portfolio', on_delete=models.CASCADE)
       profile_date = models.DateTimeField(auto_now_add=True)
       data_quality_score = models.IntegerField()
       sensitive_data_detected = models.BooleanField(default=False)
       profile_data = models.JSONField()

       def generate_profile(self):
           \"\"\"Generate fresh data profile for portfolio.\"\"\"
           service = DataProfilerService(enable_sensitive_data_detection=True)

           # Convert portfolio data to DataFrame
           transactions_df = self.portfolio.get_transactions_dataframe()

           # Analyze the data
           analysis = service.analyze_financial_data(transactions_df)

           # Store results
           self.data_quality_score = analysis['data_quality']['overall_score']
           self.sensitive_data_detected = bool(analysis['sensitive_data_detected'])
           self.profile_data = analysis
           self.save()

           return analysis

Automated Profiling Pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set up automated data profiling with Celery:

.. code-block:: python

   from celery import shared_task
   from personal_finance.data_profiler import DataProfilerService

   @shared_task
   def profile_user_portfolio(user_id):
       \"\"\"Profile user's portfolio data for quality and security.\"\"\"
       from django.contrib.auth.models import User

       try:
           user = User.objects.get(id=user_id)
           service = DataProfilerService(enable_sensitive_data_detection=True)

           # Get user's financial data
           portfolio_data = user.get_portfolio_dataframe()

           # Perform comprehensive analysis
           analysis = service.analyze_financial_data(portfolio_data)

           # Check for issues requiring attention
           quality_score = analysis['data_quality']['overall_score']
           sensitive_data = analysis['sensitive_data_detected']

           if quality_score < 70:
               send_data_quality_alert.delay(user_id, quality_score)

           if sensitive_data:
               send_sensitive_data_alert.delay(user_id, sensitive_data)

           # Store results
           PortfolioDataProfile.objects.create(
               user=user,
               data_quality_score=quality_score,
               sensitive_data_detected=bool(sensitive_data),
               profile_data=analysis
           )

       except Exception as e:
           logger.error(f\"Portfolio profiling failed for user {user_id}: {e}\")

   @shared_task
   def weekly_data_quality_check():
       \"\"\"Weekly data quality assessment for all active portfolios.\"\"\"
       from django.contrib.auth.models import User

       active_users = User.objects.filter(
           is_active=True,
           portfolios__isnull=False
       ).distinct()

       for user in active_users:
           profile_user_portfolio.delay(user.id)

API Integration
~~~~~~~~~~~~~~

Create REST API endpoints for data profiling:

.. code-block:: python

   from rest_framework import viewsets, status
   from rest_framework.decorators import action
   from rest_framework.response import Response
   from personal_finance.data_profiler import DataProfilerService, ProfileDataError

   class DataProfileViewSet(viewsets.ViewSet):
       \"\"\"API endpoints for data profiling functionality.\"\"\"

       @action(detail=False, methods=['post'])
       def analyze_upload(self, request):
           \"\"\"Analyze uploaded financial data file.\"\"\"
           if 'file' not in request.FILES:
               return Response(
                   {'error': 'No file provided'},
                   status=status.HTTP_400_BAD_REQUEST
               )

           uploaded_file = request.FILES['file']

           try:
               service = DataProfilerService(enable_sensitive_data_detection=True)

               # Analyze the uploaded data
               analysis = service.analyze_financial_data(uploaded_file.temporary_file_path())

               return Response({
                   'status': 'success',
                   'analysis': analysis,
                   'recommendations': self._generate_recommendations(analysis)
               })

           except ProfileDataError as e:
               return Response(
                   {'error': f'Data validation failed: {str(e)}'},
                   status=status.HTTP_400_BAD_REQUEST
               )
           except Exception as e:
               return Response(
                   {'error': f'Analysis failed: {str(e)}'},
                   status=status.HTTP_500_INTERNAL_SERVER_ERROR
               )

       @action(detail=False, methods=['get'])
       def portfolio_quality(self, request):
           \"\"\"Get data quality metrics for user's portfolio.\"\"\"
           try:
               portfolio_df = request.user.get_portfolio_dataframe()
               service = DataProfilerService()

               analysis = service.analyze_financial_data(portfolio_df)

               return Response({
                   'quality_score': analysis['data_quality']['overall_score'],
                   'issues': analysis['data_quality']['issues'],
                   'recommendations': self._generate_quality_recommendations(analysis)
               })

           except Exception as e:
               return Response(
                   {'error': f'Quality analysis failed: {str(e)}'},
                   status=status.HTTP_500_INTERNAL_SERVER_ERROR
               )

Error Handling and Troubleshooting
----------------------------------

Common Error Scenarios
~~~~~~~~~~~~~~~~~~~~~~

**Installation Issues**

.. code-block:: python

   # Check if DataProfiler is available
   service = DataProfilerService()

   if not service.is_available():
       print(\"❌ DataProfiler not available\")
       print(\"Install with: pip install dataprofiler\")
       print(\"For ML features: pip install dataprofiler[ml]\")

**Data Validation Errors**

.. code-block:: python

   try:
       validate_profile_data(problematic_data)
   except ProfileDataError as e:
       print(f\"Validation error: {e}\")

       # Common fixes
       if \"empty\" in str(e).lower():
           print(\"Fix: Ensure data is not empty\")
       elif \"schema\" in str(e).lower():
           print(\"Fix: Ensure consistent column names across records\")
       elif \"dimension\" in str(e).lower():
           print(\"Fix: Reshape data to 2D or less\")

**Memory Issues with Large Data**

.. code-block:: python

   try:
       analysis = service.analyze_financial_data(very_large_df)
   except MemoryError:
       print(\"Memory error - using sampling approach\")

       # Sample the data
       sample_size = min(10000, len(very_large_df))
       sample_df = very_large_df.sample(n=sample_size, random_state=42)

       analysis = service.analyze_financial_data(sample_df)
       print(f\"Analyzed {sample_size} records from {len(very_large_df)} total\")

Debug Mode and Logging
~~~~~~~~~~~~~~~~~~~~~

Enable comprehensive debugging:

.. code-block:: python

   import logging

   # Enable debug logging for data profiler
   logging.getLogger('personal_finance.data_profiler').setLevel(logging.DEBUG)

   # Enable DataProfiler internal logging
   logging.getLogger('dataprofiler').setLevel(logging.INFO)

   # Create console handler for immediate feedback
   console_handler = logging.StreamHandler()
   console_handler.setLevel(logging.DEBUG)
   formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
   console_handler.setFormatter(formatter)

   logger = logging.getLogger('personal_finance.data_profiler')
   logger.addHandler(console_handler)

Performance Monitoring
~~~~~~~~~~~~~~~~~~~~~~

Monitor profiling performance:

.. code-block:: python

   import time
   from functools import wraps

   def profile_timing(func):
       \"\"\"Decorator to measure profiling performance.\"\"\"
       @wraps(func)
       def wrapper(*args, **kwargs):
           start_time = time.time()
           result = func(*args, **kwargs)
           end_time = time.time()

           print(f\"{func.__name__} took {end_time - start_time:.2f} seconds\")
           return result
       return wrapper

   # Usage
   @profile_timing
   def analyze_large_portfolio(portfolio_data):
       service = DataProfilerService()
       return service.analyze_financial_data(portfolio_data)

Testing Framework
-----------------

Unit Testing Data Profiling
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Comprehensive testing framework for data profiling functionality:

.. code-block:: python

   import unittest
   import pandas as pd
   from personal_finance.data_profiler import DataProfilerService, validate_profile_data, ProfileDataError

   class TestDataProfiling(unittest.TestCase):
       \"\"\"Test suite for data profiling functionality.\"\"\"

       def setUp(self):
           self.service = DataProfilerService(enable_sensitive_data_detection=True)

           self.sample_financial_data = pd.DataFrame({
               'transaction_id': ['TXN001', 'TXN002', 'TXN003'],
               'amount': [100.50, -250.75, 1500.00],
               'date': ['2024-01-15', '2024-01-16', '2024-01-17'],
               'description': ['Purchase', 'Sale', 'Dividend']
           })

       def test_valid_dataframe_validation(self):
           \"\"\"Test validation passes for valid DataFrame.\"\"\"
           try:
               validate_profile_data(self.sample_financial_data)
           except ProfileDataError:
               self.fail(\"Valid DataFrame should not raise ProfileDataError\")

       def test_empty_dataframe_validation(self):
           \"\"\"Test validation fails for empty DataFrame.\"\"\"
           empty_df = pd.DataFrame()

           with self.assertRaises(ProfileDataError) as context:
               validate_profile_data(empty_df)

           self.assertIn(\"empty\", str(context.exception).lower())

       def test_financial_pattern_detection(self):
           \"\"\"Test financial pattern detection.\"\"\"
           analysis = self.service.analyze_financial_data(self.sample_financial_data)

           # Should detect amount column
           patterns = analysis['financial_patterns']
           self.assertIn('amount', patterns['potential_currency_columns'])

           # Should detect date column
           self.assertIn('date', patterns['potential_date_columns'])

       def test_sensitive_data_detection(self):
           \"\"\"Test sensitive data detection.\"\"\"
           sensitive_data = pd.DataFrame({
               'account': ['1234567890', '9876543210'],
               'ssn': ['123-45-6789', '987-65-4321'],
               'amount': [1000, 2000]
           })

           analysis = self.service.analyze_financial_data(sensitive_data)
           sensitive_findings = analysis['sensitive_data_detected']

           # Should detect potential SSN
           ssn_detected = any(
               finding['pattern_type'] == 'potential_ssn'
               for finding in sensitive_findings
           )
           self.assertTrue(ssn_detected, \"SSN pattern should be detected\")

       def test_data_quality_analysis(self):
           \"\"\"Test data quality analysis.\"\"\"
           # Create data with quality issues
           quality_test_data = pd.DataFrame({
               'col1': [1, 2, None, 4, 5],  # Missing data
               'col2': [1, 1, 1, 1, 1],     # Constant values
               'col3': [1, 2, 1, 2, 1000],  # Outlier
               'col4': ['A', 'B', 'A', 'B', 'A']  # No issues
           })

           analysis = self.service.analyze_financial_data(quality_test_data)
           quality = analysis['data_quality']

           # Should detect missing data
           self.assertGreater(quality['missing_data_ratio'], 0)

           # Should detect constant column
           self.assertIn('col2', quality['constant_columns'])

           # Should detect potential outliers
           outlier_columns = [col['column'] for col in quality['outlier_candidates']]
           self.assertIn('col3', outlier_columns)

Best Practices
--------------

For Developers
~~~~~~~~~~~~~~

1. **Always Validate Before Profiling**

   .. code-block:: python

      # Good practice
      try:
          validate_profile_data(financial_data)
          analysis = service.analyze_financial_data(financial_data)
      except ProfileDataError as e:
          logger.error(f\"Data validation failed: {e}\")
          return None

      # Avoid this
      analysis = service.analyze_financial_data(financial_data)  # May fail unexpectedly

2. **Use Data Preparation for Performance**

   .. code-block:: python

      # Optimize data format before processing
      prepared_data = validate_and_prepare_data(raw_financial_records)
      analysis = service.analyze_financial_data(prepared_data)

3. **Handle Missing DataProfiler Gracefully**

   .. code-block:: python

      service = DataProfilerService()

      if not service.is_available():
          logger.warning(\"DataProfiler not available, using limited analysis\")
          # Implement fallback analysis
          return basic_financial_analysis(data)

4. **Enable Sensitive Data Detection for Financial Applications**

   .. code-block:: python

      # For financial data processing
      service = DataProfilerService(enable_sensitive_data_detection=True)

      analysis = service.analyze_financial_data(financial_data)
      if analysis['sensitive_data_detected']:
          handle_sensitive_data_findings(analysis['sensitive_data_detected'])

For System Administrators
~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Monitor Resource Usage**

   .. code-block:: bash

      # Monitor memory usage during profiling
      pip install memory-profiler
      mprof run python manage.py profile_portfolios
      mprof plot

2. **Schedule Regular Data Quality Checks**

   .. code-block:: python

      # Set up automated monitoring
      @shared_task(cron='0 2 * * 0')  # Weekly at 2 AM
      def weekly_data_quality_monitoring():
          check_all_portfolio_quality()

3. **Implement Data Quality Alerts**

   .. code-block:: python

      def check_data_quality_thresholds(analysis):
          quality_score = analysis['data_quality']['overall_score']

          if quality_score < 60:
              send_urgent_data_quality_alert(analysis)
          elif quality_score < 80:
              send_data_quality_warning(analysis)

Security Considerations
-----------------------

Sensitive Data Handling
~~~~~~~~~~~~~~~~~~~~~~~

1. **Never Log Sensitive Data**

   .. code-block:: python

      # Good - log without sensitive details
      logger.info(f\"Sensitive data detected in {len(findings)} columns\")

      # Bad - logs actual sensitive data
      logger.info(f\"SSN found: {ssn_value}\")

2. **Implement Data Masking**

   .. code-block:: python

      def mask_sensitive_findings(findings):
          \"\"\"Mask sensitive data in findings for safe logging/display.\"\"\"
          masked_findings = []

          for finding in findings:
              masked_finding = finding.copy()
              if 'examples' in masked_finding:
                  masked_finding['examples'] = ['***MASKED***'] * len(finding['examples'])
              masked_findings.append(masked_finding)

          return masked_findings

3. **Access Control for Profiling Results**

   .. code-block:: python

      class DataProfileView(APIView):
          permission_classes = [IsAuthenticated, HasDataProfilePermission]

          def get(self, request):
              # Only return appropriate detail level based on permissions
              if request.user.has_perm('data_profiler.view_sensitive'):
                  return full_analysis
              else:
                  return sanitized_analysis

See Also
--------

* :doc:`../api/rest_endpoints` - REST API integration for data profiling
* :doc:`../modules/portfolio` - Portfolio data integration
* :doc:`../config/security` - Security configuration for sensitive data
* :doc:`../development/testing` - Testing framework for data profiling features
