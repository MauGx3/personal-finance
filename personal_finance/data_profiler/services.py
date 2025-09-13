"""DataProfiler service for financial data analysis and sensitive data detection.

This module provides integration with the DataProfiler library for analyzing
financial data, detecting PII/sensitive information, and generating comprehensive
data quality reports.
"""

import logging
from typing import Any, Dict, Optional, Union, List
from decimal import Decimal
import pandas as pd
import numpy as np

from .validators import validate_profile_data, validate_and_prepare_data, ProfileDataError

logger = logging.getLogger(__name__)


class DataProfilerService:
    """Service class for DataProfiler integration with validation.
    
    This class provides a safe wrapper around DataProfiler functionality,
    ensuring data compatibility and providing financial-specific profiling features.
    """
    
    def __init__(self, enable_sensitive_data_detection: bool = True):
        """Initialize DataProfiler service.
        
        Args:
            enable_sensitive_data_detection: Whether to enable PII/sensitive data detection
        """
        self.enable_sensitive_data_detection = enable_sensitive_data_detection
        self._profiler = None
        
        # Try to import DataProfiler, gracefully handle if not available
        try:
            import dataprofiler as dp
            self._dp_module = dp
            self._dp_available = True
            logger.info("DataProfiler module loaded successfully")
        except ImportError:
            self._dp_module = None
            self._dp_available = False
            logger.warning(
                "DataProfiler not available. Install with: pip install dataprofiler"
            )
    
    def is_available(self) -> bool:
        """Check if DataProfiler is available for use.
        
        Returns:
            bool: True if DataProfiler is available, False otherwise
        """
        return self._dp_available
    
    def create_profile(self, profile_data: Any, **kwargs) -> Optional[Dict[str, Any]]:
        """Create a data profile with validation.
        
        This method validates the input data before passing it to DataProfiler,
        preventing constructor failures due to incompatible data formats.
        
        Args:
            profile_data: Data to profile (DataFrame, array, file path, etc.)
            **kwargs: Additional arguments to pass to DataProfiler
            
        Returns:
            Dictionary containing profile results or None if DataProfiler unavailable
            
        Raises:
            ProfileDataError: If data is not compatible with DataProfiler
            
        Example:
            >>> service = DataProfilerService()
            >>> df = pd.DataFrame({'amount': [100, 200, 300], 'type': ['buy', 'sell', 'buy']})
            >>> profile = service.create_profile(df)
            >>> print(profile['summary'])
        """
        if not self._dp_available:
            logger.error("DataProfiler is not available")
            return None
        
        try:
            # Validate and prepare the data
            validated_data = validate_and_prepare_data(profile_data)
            logger.info("Data validation successful, creating profile")
            
            # Configure DataProfiler options
            profiler_options = self._get_profiler_options(**kwargs)
            
            # Create the profiler with validated data
            self._profiler = self._dp_module.Profiler(
                data=validated_data,
                **profiler_options
            )
            
            # Generate the profile report
            profile_report = self._extract_profile_results()
            
            logger.info("Profile created successfully")
            return profile_report
            
        except ProfileDataError:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Error creating DataProfiler profile: {e}")
            raise ProfileDataError(f"Failed to create profile: {e}")
    
    def analyze_financial_data(self, financial_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze financial data with domain-specific insights.
        
        This method provides financial-specific analysis on top of basic profiling,
        including detection of financial patterns, anomalies, and data quality issues.
        
        Args:
            financial_data: DataFrame containing financial data
            
        Returns:
            Dictionary with financial-specific analysis results
        """
        if not isinstance(financial_data, pd.DataFrame):
            raise ProfileDataError("Financial data must be a pandas DataFrame")
        
        # Validate the financial data
        validate_profile_data(financial_data)
        
        analysis_results = {
            'basic_profile': None,
            'financial_patterns': {},
            'data_quality': {},
            'sensitive_data_detected': []
        }
        
        # Basic profiling if DataProfiler is available
        if self._dp_available:
            try:
                analysis_results['basic_profile'] = self.create_profile(financial_data)
            except Exception as e:
                logger.warning(f"Basic profiling failed: {e}")
        
        # Financial-specific analysis
        analysis_results['financial_patterns'] = self._analyze_financial_patterns(financial_data)
        analysis_results['data_quality'] = self._analyze_data_quality(financial_data)
        
        # Sensitive data detection
        if self.enable_sensitive_data_detection:
            analysis_results['sensitive_data_detected'] = self._detect_sensitive_financial_data(
                financial_data
            )
        
        return analysis_results
    
    def _get_profiler_options(self, **kwargs) -> Dict[str, Any]:
        """Get DataProfiler configuration options.
        
        Args:
            **kwargs: User-provided options
            
        Returns:
            Dictionary of profiler options
        """
        default_options = {
            'samples_per_update': None,  # Process all data
            'min_true_samples': 0,  # No minimum sample requirement
        }
        
        # Override defaults with user options
        profiler_options = {**default_options, **kwargs}
        
        # Configure sensitive data detection
        if not self.enable_sensitive_data_detection:
            profiler_options['options'] = {
                'data_labeler.is_enabled': False
            }
        
        return profiler_options
    
    def _extract_profile_results(self) -> Dict[str, Any]:
        """Extract and format results from DataProfiler.
        
        Returns:
            Formatted profile results dictionary
        """
        if not self._profiler:
            return {}
        
        try:
            # Get the profile report
            profile_report = self._profiler.report()
            
            # Extract key metrics
            results = {
                'summary': self._extract_summary_stats(profile_report),
                'column_profiles': self._extract_column_profiles(profile_report),
                'data_types': self._extract_data_types(profile_report),
                'null_analysis': self._extract_null_analysis(profile_report),
                'sensitive_data': self._extract_sensitive_data(profile_report),
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error extracting profile results: {e}")
            return {'error': str(e)}
    
    def _extract_summary_stats(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Extract summary statistics from profile report.
        
        Args:
            report: DataProfiler report
            
        Returns:
            Summary statistics dictionary
        """
        try:
            global_stats = report.get('global_stats', {})
            return {
                'total_samples': global_stats.get('samples_used', 0),
                'total_columns': global_stats.get('column_count', 0),
                'memory_size': global_stats.get('memory_size', 0),
                'file_type': global_stats.get('file_type', 'unknown'),
                'encoding': global_stats.get('encoding', 'unknown'),
            }
        except Exception as e:
            logger.warning(f"Error extracting summary stats: {e}")
            return {}
    
    def _extract_column_profiles(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Extract column-specific profiles from report.
        
        Args:
            report: DataProfiler report
            
        Returns:
            Column profiles dictionary
        """
        try:
            data_stats = report.get('data_stats', [])
            column_profiles = {}
            
            for col_stat in data_stats:
                col_name = col_stat.get('column_name', 'unknown')
                column_profiles[col_name] = {
                    'data_type': col_stat.get('data_type', 'unknown'),
                    'statistics': col_stat.get('statistics', {}),
                    'null_count': col_stat.get('null_count', 0),
                    'null_ratio': col_stat.get('null_ratio', 0.0),
                }
            
            return column_profiles
            
        except Exception as e:
            logger.warning(f"Error extracting column profiles: {e}")
            return {}
    
    def _extract_data_types(self, report: Dict[str, Any]) -> Dict[str, str]:
        """Extract detected data types for each column.
        
        Args:
            report: DataProfiler report
            
        Returns:
            Dictionary mapping column names to detected types
        """
        try:
            data_stats = report.get('data_stats', [])
            return {
                col_stat.get('column_name', 'unknown'): col_stat.get('data_type', 'unknown')
                for col_stat in data_stats
            }
        except Exception as e:
            logger.warning(f"Error extracting data types: {e}")
            return {}
    
    def _extract_null_analysis(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Extract null value analysis from report.
        
        Args:
            report: DataProfiler report
            
        Returns:
            Null analysis dictionary
        """
        try:
            data_stats = report.get('data_stats', [])
            null_analysis = {}
            
            for col_stat in data_stats:
                col_name = col_stat.get('column_name', 'unknown')
                null_analysis[col_name] = {
                    'null_count': col_stat.get('null_count', 0),
                    'null_ratio': col_stat.get('null_ratio', 0.0),
                    'total_count': col_stat.get('sample_size', 0),
                }
            
            return null_analysis
            
        except Exception as e:
            logger.warning(f"Error extracting null analysis: {e}")
            return {}
    
    def _extract_sensitive_data(self, report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract sensitive data detection results.
        
        Args:
            report: DataProfiler report
            
        Returns:
            List of sensitive data findings
        """
        if not self.enable_sensitive_data_detection:
            return []
        
        try:
            # Extract sensitive data findings from the report
            # This will depend on the specific DataProfiler version and configuration
            sensitive_findings = []
            
            data_stats = report.get('data_stats', [])
            for col_stat in data_stats:
                col_name = col_stat.get('column_name', 'unknown')
                data_label = col_stat.get('data_label', {})
                
                if data_label and data_label != 'UNKNOWN':
                    sensitive_findings.append({
                        'column': col_name,
                        'data_label': data_label,
                        'confidence': col_stat.get('data_label_probability', 0.0),
                    })
            
            return sensitive_findings
            
        except Exception as e:
            logger.warning(f"Error extracting sensitive data findings: {e}")
            return []
    
    def _analyze_financial_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze financial-specific patterns in the data.
        
        Args:
            df: Financial data DataFrame
            
        Returns:
            Financial patterns analysis
        """
        patterns = {
            'potential_currency_columns': [],
            'potential_date_columns': [],
            'potential_amount_columns': [],
            'suspicious_patterns': []
        }
        
        for col in df.columns:
            col_data = df[col].dropna()
            if col_data.empty:
                continue
            
            # Check for currency patterns
            if self._looks_like_currency_column(col, col_data):
                patterns['potential_currency_columns'].append(col)
            
            # Check for date patterns
            if self._looks_like_date_column(col, col_data):
                patterns['potential_date_columns'].append(col)
            
            # Check for amount patterns
            if self._looks_like_amount_column(col, col_data):
                patterns['potential_amount_columns'].append(col)
            
            # Check for suspicious patterns
            suspicious = self._check_suspicious_patterns(col, col_data)
            if suspicious:
                patterns['suspicious_patterns'].extend(suspicious)
        
        return patterns
    
    def _analyze_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data quality issues in financial data.
        
        Args:
            df: Financial data DataFrame
            
        Returns:
            Data quality analysis
        """
        quality_issues = {
            'missing_data_ratio': df.isnull().sum().sum() / (len(df) * len(df.columns)),
            'duplicate_rows': df.duplicated().sum(),
            'empty_columns': [col for col in df.columns if df[col].isnull().all()],
            'constant_columns': [col for col in df.columns if df[col].nunique() <= 1],
            'outlier_candidates': []
        }
        
        # Check for potential outliers in numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                q1 = col_data.quantile(0.25)
                q3 = col_data.quantile(0.75)
                iqr = q3 - q1
                outlier_count = ((col_data < q1 - 1.5 * iqr) | (col_data > q3 + 1.5 * iqr)).sum()
                if outlier_count > 0:
                    quality_issues['outlier_candidates'].append({
                        'column': col,
                        'outlier_count': outlier_count,
                        'outlier_ratio': outlier_count / len(col_data)
                    })
        
        return quality_issues
    
    def _detect_sensitive_financial_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect potentially sensitive financial information.
        
        Args:
            df: Financial data DataFrame
            
        Returns:
            List of sensitive data detections
        """
        sensitive_patterns = []
        
        for col in df.columns:
            col_data = df[col].astype(str).dropna()
            if col_data.empty:
                continue
            
            # Check for account numbers (simplified pattern)
            if any(len(str(val).replace('-', '').replace(' ', '')) >= 8 and 
                   str(val).replace('-', '').replace(' ', '').isdigit() 
                   for val in col_data.head(10)):
                sensitive_patterns.append({
                    'column': col,
                    'pattern_type': 'potential_account_number',
                    'confidence': 0.7,
                    'recommendation': 'Consider masking or encrypting this column'
                })
            
            # Check for SSN-like patterns
            if any(self._looks_like_ssn(str(val)) for val in col_data.head(10)):
                sensitive_patterns.append({
                    'column': col,
                    'pattern_type': 'potential_ssn',
                    'confidence': 0.8,
                    'recommendation': 'High sensitivity - should be encrypted or removed'
                })
        
        return sensitive_patterns
    
    def _looks_like_currency_column(self, col_name: str, col_data: pd.Series) -> bool:
        """Check if column looks like currency data."""
        currency_keywords = ['amount', 'price', 'cost', 'value', 'balance', 'fee', 'charge']
        return any(keyword in col_name.lower() for keyword in currency_keywords)
    
    def _looks_like_date_column(self, col_name: str, col_data: pd.Series) -> bool:
        """Check if column looks like date data."""
        date_keywords = ['date', 'time', 'created', 'updated', 'timestamp']
        return any(keyword in col_name.lower() for keyword in date_keywords)
    
    def _looks_like_amount_column(self, col_name: str, col_data: pd.Series) -> bool:
        """Check if column contains financial amounts."""
        try:
            # Check if numeric and has reasonable decimal precision for money
            if col_data.dtype in ['float64', 'int64'] or pd.api.types.is_numeric_dtype(col_data):
                return True
        except:
            pass
        return False
    
    def _check_suspicious_patterns(self, col_name: str, col_data: pd.Series) -> List[Dict[str, Any]]:
        """Check for suspicious patterns in the data."""
        suspicious = []
        
        # Check for extremely high values that might be data entry errors
        if pd.api.types.is_numeric_dtype(col_data):
            max_val = col_data.max()
            if max_val > 1e9:  # Values over 1 billion
                suspicious.append({
                    'column': col_name,
                    'issue': 'extremely_high_values',
                    'max_value': float(max_val),
                    'recommendation': 'Verify if high values are legitimate'
                })
        
        return suspicious
    
    def _looks_like_ssn(self, value: str) -> bool:
        """Check if value looks like a Social Security Number."""
        # Simple pattern: XXX-XX-XXXX or XXXXXXXXX
        value = str(value).replace('-', '').replace(' ', '')
        return len(value) == 9 and value.isdigit()