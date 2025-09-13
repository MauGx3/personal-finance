"""Tests for DataProfiler service functionality."""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

from personal_finance.data_profiler.services import DataProfilerService
from personal_finance.data_profiler.validators import ProfileDataError


class TestDataProfilerService:
    """Test cases for DataProfiler service."""
    
    def test_service_initialization_with_dataprofiler_available(self):
        """Test service initialization when DataProfiler is available."""
        with patch('personal_finance.data_profiler.services.logger') as mock_logger:
            with patch('personal_finance.data_profiler.services.DataProfilerService.__init__') as mock_init:
                mock_init.return_value = None
                service = DataProfilerService()
                # Mock the initialization to simulate DataProfiler being available
                service._dp_available = True
                service._dp_module = MagicMock()
                
                assert service.is_available() is True
    
    def test_service_initialization_without_dataprofiler(self):
        """Test service initialization when DataProfiler is not available."""
        with patch('builtins.__import__', side_effect=ImportError("No module named 'dataprofiler'")):
            with patch('personal_finance.data_profiler.services.logger') as mock_logger:
                service = DataProfilerService()
                assert service.is_available() is False
                mock_logger.warning.assert_called_with(
                    "DataProfiler not available. Install with: pip install dataprofiler"
                )
    
    def test_create_profile_without_dataprofiler_returns_none(self):
        """Test that create_profile returns None when DataProfiler is unavailable."""
        service = DataProfilerService()
        service._dp_available = False
        
        df = pd.DataFrame({'col1': [1, 2, 3]})
        
        with patch('personal_finance.data_profiler.services.logger') as mock_logger:
            result = service.create_profile(df)
            assert result is None
            mock_logger.error.assert_called_with("DataProfiler is not available")
    
    def test_create_profile_with_invalid_data_raises_error(self):
        """Test that create_profile raises error for invalid data."""
        service = DataProfilerService()
        service._dp_available = True
        service._dp_module = MagicMock()
        
        with pytest.raises(ProfileDataError):
            service.create_profile(None)
    
    def test_create_profile_success_path(self):
        """Test successful profile creation."""
        service = DataProfilerService()
        service._dp_available = True
        
        # Mock DataProfiler module
        mock_dp_module = MagicMock()
        mock_profiler = MagicMock()
        mock_dp_module.Profiler.return_value = mock_profiler
        service._dp_module = mock_dp_module
        
        # Mock profile report
        mock_report = {
            'global_stats': {
                'samples_used': 3,
                'column_count': 2,
                'memory_size': 1024,
                'file_type': 'csv',
                'encoding': 'utf-8'
            },
            'data_stats': [
                {
                    'column_name': 'col1',
                    'data_type': 'int',
                    'statistics': {'mean': 2.0},
                    'null_count': 0,
                    'null_ratio': 0.0,
                    'sample_size': 3,
                    'data_label': 'INTEGER',
                    'data_label_probability': 0.95
                }
            ]
        }
        mock_profiler.report.return_value = mock_report
        
        df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
        
        with patch('personal_finance.data_profiler.services.logger') as mock_logger:
            result = service.create_profile(df)
            
            assert result is not None
            assert 'summary' in result
            assert 'column_profiles' in result
            assert 'data_types' in result
            assert 'null_analysis' in result
            assert 'sensitive_data' in result
            
            mock_logger.info.assert_any_call("Data validation successful, creating profile")
            mock_logger.info.assert_any_call("Profile created successfully")
    
    def test_create_profile_dataprofiler_error_handling(self):
        """Test error handling during DataProfiler execution."""
        service = DataProfilerService()
        service._dp_available = True
        
        # Mock DataProfiler module to raise an exception
        mock_dp_module = MagicMock()
        mock_dp_module.Profiler.side_effect = Exception("DataProfiler error")
        service._dp_module = mock_dp_module
        
        df = pd.DataFrame({'col1': [1, 2, 3]})
        
        with pytest.raises(ProfileDataError, match="Failed to create profile"):
            service.create_profile(df)
    
    def test_analyze_financial_data_invalid_input(self):
        """Test financial data analysis with invalid input."""
        service = DataProfilerService()
        
        with pytest.raises(ProfileDataError, match="Financial data must be a pandas DataFrame"):
            service.analyze_financial_data([1, 2, 3])
    
    def test_analyze_financial_data_success(self):
        """Test successful financial data analysis."""
        service = DataProfilerService()
        service._dp_available = False  # Disable DataProfiler for simpler test
        
        financial_df = pd.DataFrame({
            'transaction_id': ['T001', 'T002', 'T003'],
            'amount': [100.50, 250.75, 75.25],
            'transaction_type': ['debit', 'credit', 'debit'],
            'account_number': ['1234567890', '0987654321', '1234567890'],
            'transaction_date': ['2024-01-15', '2024-01-16', '2024-01-17']
        })
        
        result = service.analyze_financial_data(financial_df)
        
        assert 'basic_profile' in result
        assert 'financial_patterns' in result
        assert 'data_quality' in result
        assert 'sensitive_data_detected' in result
        
        # Check financial patterns detection
        patterns = result['financial_patterns']
        assert 'potential_amount_columns' in patterns
        assert 'amount' in patterns['potential_amount_columns']
        
        # Check data quality analysis
        quality = result['data_quality']
        assert 'missing_data_ratio' in quality
        assert 'duplicate_rows' in quality
        assert 'empty_columns' in quality
        assert 'constant_columns' in quality
        assert 'outlier_candidates' in quality
    
    def test_analyze_financial_data_with_dataprofiler(self):
        """Test financial data analysis with DataProfiler enabled."""
        service = DataProfilerService()
        service._dp_available = True
        
        # Mock successful profile creation
        with patch.object(service, 'create_profile') as mock_create_profile:
            mock_create_profile.return_value = {'mock': 'profile'}
            
            financial_df = pd.DataFrame({
                'amount': [100.50, 250.75, 75.25],
                'account_id': ['ACC001', 'ACC002', 'ACC003']
            })
            
            result = service.analyze_financial_data(financial_df)
            
            assert result['basic_profile'] == {'mock': 'profile'}
            mock_create_profile.assert_called_once_with(financial_df)
    
    def test_analyze_financial_data_dataprofiler_error(self):
        """Test financial data analysis when DataProfiler fails."""
        service = DataProfilerService()
        service._dp_available = True
        
        # Mock failed profile creation
        with patch.object(service, 'create_profile') as mock_create_profile:
            mock_create_profile.side_effect = Exception("Profile creation failed")
            
            with patch('personal_finance.data_profiler.services.logger') as mock_logger:
                financial_df = pd.DataFrame({'amount': [100.50, 250.75]})
                
                result = service.analyze_financial_data(financial_df)
                
                assert result['basic_profile'] is None
                mock_logger.warning.assert_called_with("Basic profiling failed: Profile creation failed")


class TestFinancialPatternAnalysis:
    """Test financial pattern analysis methods."""
    
    def test_looks_like_currency_column(self):
        """Test currency column detection."""
        service = DataProfilerService()
        
        # Test positive cases
        assert service._looks_like_currency_column('amount', pd.Series([1, 2, 3]))
        assert service._looks_like_currency_column('price', pd.Series([1, 2, 3]))
        assert service._looks_like_currency_column('total_cost', pd.Series([1, 2, 3]))
        assert service._looks_like_currency_column('account_balance', pd.Series([1, 2, 3]))
        
        # Test negative cases
        assert not service._looks_like_currency_column('name', pd.Series(['a', 'b', 'c']))
        assert not service._looks_like_currency_column('id', pd.Series([1, 2, 3]))
    
    def test_looks_like_date_column(self):
        """Test date column detection."""
        service = DataProfilerService()
        
        # Test positive cases
        assert service._looks_like_date_column('transaction_date', pd.Series(['2024-01-01']))
        assert service._looks_like_date_column('created_at', pd.Series(['2024-01-01']))
        assert service._looks_like_date_column('timestamp', pd.Series(['2024-01-01']))
        
        # Test negative cases
        assert not service._looks_like_date_column('amount', pd.Series([1, 2, 3]))
        assert not service._looks_like_date_column('name', pd.Series(['a', 'b', 'c']))
    
    def test_looks_like_amount_column(self):
        """Test amount column detection."""
        service = DataProfilerService()
        
        # Test positive cases
        numeric_series = pd.Series([100.50, 250.75, 75.25])
        assert service._looks_like_amount_column('amount', numeric_series)
        
        int_series = pd.Series([1, 2, 3])
        assert service._looks_like_amount_column('count', int_series)
        
        # Test negative case
        string_series = pd.Series(['a', 'b', 'c'])
        assert not service._looks_like_amount_column('name', string_series)
    
    def test_check_suspicious_patterns(self):
        """Test suspicious pattern detection."""
        service = DataProfilerService()
        
        # Test extremely high values
        high_value_series = pd.Series([100, 200, 2000000000])  # 2 billion
        suspicious = service._check_suspicious_patterns('amount', high_value_series)
        
        assert len(suspicious) == 1
        assert suspicious[0]['issue'] == 'extremely_high_values'
        assert suspicious[0]['column'] == 'amount'
        assert suspicious[0]['max_value'] == 2000000000
        
        # Test normal values
        normal_series = pd.Series([100, 200, 300])
        suspicious = service._check_suspicious_patterns('amount', normal_series)
        assert len(suspicious) == 0
    
    def test_looks_like_ssn(self):
        """Test SSN pattern detection."""
        service = DataProfilerService()
        
        # Test positive cases
        assert service._looks_like_ssn('123-45-6789')
        assert service._looks_like_ssn('123456789')
        assert service._looks_like_ssn('123 45 6789')
        
        # Test negative cases
        assert not service._looks_like_ssn('12345678')  # Too short
        assert not service._looks_like_ssn('1234567890')  # Too long
        assert not service._looks_like_ssn('12a-45-6789')  # Contains letters


class TestDataQualityAnalysis:
    """Test data quality analysis methods."""
    
    def test_analyze_data_quality_comprehensive(self):
        """Test comprehensive data quality analysis."""
        service = DataProfilerService()
        
        # Create a DataFrame with various data quality issues
        df = pd.DataFrame({
            'good_column': [1, 2, 3, 4, 5],
            'missing_data': [1, None, 3, None, 5],
            'empty_column': [None, None, None, None, None],
            'constant_column': [1, 1, 1, 1, 1],
            'outlier_column': [1, 2, 3, 4, 1000],  # 1000 is an outlier
            'duplicate_row_data': [1, 1, 2, 2, 3]
        })
        
        # Add duplicate rows
        df = pd.concat([df, df.iloc[[0, 1]]], ignore_index=True)
        
        quality = service._analyze_data_quality(df)
        
        # Check missing data ratio
        assert quality['missing_data_ratio'] > 0
        
        # Check duplicate rows
        assert quality['duplicate_rows'] == 2
        
        # Check empty columns
        assert 'empty_column' in quality['empty_columns']
        
        # Check constant columns
        assert 'constant_column' in quality['constant_columns']
        
        # Check outliers
        assert len(quality['outlier_candidates']) > 0
        outlier_col = quality['outlier_candidates'][0]
        assert outlier_col['column'] == 'outlier_column'
        assert outlier_col['outlier_count'] > 0


class TestSensitiveDataDetection:
    """Test sensitive data detection methods."""
    
    def test_detect_sensitive_financial_data(self):
        """Test detection of sensitive financial information."""
        service = DataProfilerService(enable_sensitive_data_detection=True)
        
        df = pd.DataFrame({
            'name': ['John Doe', 'Jane Smith'],
            'account_number': ['1234567890', '0987654321'],
            'ssn': ['123-45-6789', '987-65-4321'],
            'amount': [100.50, 250.75]
        })
        
        sensitive_data = service._detect_sensitive_financial_data(df)
        
        # Should detect account numbers and SSNs
        assert len(sensitive_data) >= 2
        
        # Check for account number detection
        account_findings = [s for s in sensitive_data if s['pattern_type'] == 'potential_account_number']
        assert len(account_findings) > 0
        assert account_findings[0]['column'] == 'account_number'
        
        # Check for SSN detection
        ssn_findings = [s for s in sensitive_data if s['pattern_type'] == 'potential_ssn']
        assert len(ssn_findings) > 0
        assert ssn_findings[0]['column'] == 'ssn'
    
    def test_sensitive_data_detection_disabled(self):
        """Test that sensitive data detection can be disabled."""
        service = DataProfilerService(enable_sensitive_data_detection=False)
        
        df = pd.DataFrame({
            'ssn': ['123-45-6789', '987-65-4321']
        })
        
        result = service.analyze_financial_data(df)
        assert result['sensitive_data_detected'] == []


class TestProfilerOptions:
    """Test DataProfiler configuration options."""
    
    def test_get_profiler_options_default(self):
        """Test default profiler options."""
        service = DataProfilerService()
        
        options = service._get_profiler_options()
        
        assert 'samples_per_update' in options
        assert 'min_true_samples' in options
        assert options['samples_per_update'] is None
        assert options['min_true_samples'] == 0
    
    def test_get_profiler_options_with_user_options(self):
        """Test profiler options with user overrides."""
        service = DataProfilerService()
        
        user_options = {
            'samples_per_update': 1000,
            'custom_option': 'custom_value'
        }
        
        options = service._get_profiler_options(**user_options)
        
        assert options['samples_per_update'] == 1000
        assert options['custom_option'] == 'custom_value'
        assert options['min_true_samples'] == 0  # Default preserved
    
    def test_get_profiler_options_sensitive_data_disabled(self):
        """Test profiler options when sensitive data detection is disabled."""
        service = DataProfilerService(enable_sensitive_data_detection=False)
        
        options = service._get_profiler_options()
        
        assert 'options' in options
        assert options['options']['data_labeler.is_enabled'] is False


class TestProfileResultExtraction:
    """Test profile result extraction methods."""
    
    def test_extract_profile_results_no_profiler(self):
        """Test profile extraction when no profiler exists."""
        service = DataProfilerService()
        service._profiler = None
        
        result = service._extract_profile_results()
        assert result == {}
    
    def test_extract_summary_stats(self):
        """Test summary statistics extraction."""
        service = DataProfilerService()
        
        mock_report = {
            'global_stats': {
                'samples_used': 1000,
                'column_count': 5,
                'memory_size': 2048,
                'file_type': 'csv',
                'encoding': 'utf-8'
            }
        }
        
        summary = service._extract_summary_stats(mock_report)
        
        assert summary['total_samples'] == 1000
        assert summary['total_columns'] == 5
        assert summary['memory_size'] == 2048
        assert summary['file_type'] == 'csv'
        assert summary['encoding'] == 'utf-8'
    
    def test_extract_column_profiles(self):
        """Test column profile extraction."""
        service = DataProfilerService()
        
        mock_report = {
            'data_stats': [
                {
                    'column_name': 'amount',
                    'data_type': 'float',
                    'statistics': {'mean': 150.5, 'std': 75.2},
                    'null_count': 2,
                    'null_ratio': 0.1
                },
                {
                    'column_name': 'name',
                    'data_type': 'string',
                    'statistics': {'unique_count': 18},
                    'null_count': 0,
                    'null_ratio': 0.0
                }
            ]
        }
        
        profiles = service._extract_column_profiles(mock_report)
        
        assert 'amount' in profiles
        assert 'name' in profiles
        assert profiles['amount']['data_type'] == 'float'
        assert profiles['amount']['null_count'] == 2
        assert profiles['name']['data_type'] == 'string'
        assert profiles['name']['null_count'] == 0
    
    def test_extract_sensitive_data_disabled(self):
        """Test sensitive data extraction when disabled."""
        service = DataProfilerService(enable_sensitive_data_detection=False)
        
        mock_report = {'data_stats': []}
        
        sensitive_data = service._extract_sensitive_data(mock_report)
        assert sensitive_data == []


class TestIntegrationScenarios:
    """Integration test scenarios."""
    
    def test_full_financial_analysis_workflow(self):
        """Test complete financial data analysis workflow."""
        service = DataProfilerService(enable_sensitive_data_detection=True)
        service._dp_available = False  # Disable DataProfiler for predictable testing
        
        # Create realistic financial dataset
        financial_data = pd.DataFrame({
            'transaction_id': ['TXN001', 'TXN002', 'TXN003', 'TXN004'],
            'account_number': ['1234567890', '0987654321', '1234567890', '5555555555'],
            'amount': [1500.75, 250.00, 75.50, 10000.00],  # Last amount is suspicious
            'transaction_type': ['credit', 'debit', 'debit', 'credit'],
            'transaction_date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18'],
            'description': ['Salary deposit', 'Grocery store', 'Coffee shop', 'Investment return']
        })
        
        result = service.analyze_financial_data(financial_data)
        
        # Verify all components are present
        assert 'basic_profile' in result
        assert 'financial_patterns' in result
        assert 'data_quality' in result
        assert 'sensitive_data_detected' in result
        
        # Verify financial pattern detection
        patterns = result['financial_patterns']
        assert 'amount' in patterns['potential_amount_columns']
        assert 'transaction_date' in patterns['potential_date_columns']
        
        # Verify sensitive data detection
        sensitive_data = result['sensitive_data_detected']
        account_number_findings = [
            s for s in sensitive_data 
            if s['pattern_type'] == 'potential_account_number'
        ]
        assert len(account_number_findings) > 0
        
        # Verify data quality analysis
        quality = result['data_quality']
        assert quality['duplicate_rows'] == 0  # No duplicate rows
        assert len(quality['empty_columns']) == 0  # No empty columns
        assert len(quality['constant_columns']) == 0  # No constant columns