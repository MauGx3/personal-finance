"""Data profiling and sensitive data detection for personal finance platform.

This module integrates DataProfiler for automatic data analysis, monitoring,
and sensitive data detection as specified in the S.C.A.F.F. structure requirements.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from decimal import Decimal

try:
    import dataprofiler as dp
    DATAPROFILER_AVAILABLE = True
except ImportError:
    DATAPROFILER_AVAILABLE = False
    dp = None

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False
    pl = None

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


class FinancialDataProfiler:
    """Financial data profiler with sensitive data detection capabilities.
    
    Integrates DataProfiler for comprehensive data analysis including:
    - Automatic schema detection
    - Statistical profiling
    - Sensitive data (PII/NPI) detection
    - Data quality assessment
    """
    
    def __init__(self):
        """Initialize the data profiler with available libraries."""
        self.dataprofiler_available = DATAPROFILER_AVAILABLE
        self.pandas_available = PANDAS_AVAILABLE
        self.polars_available = POLARS_AVAILABLE
        
        if not self.dataprofiler_available:
            logger.warning(
                "DataProfiler not available. Install with: pip install DataProfiler"
            )
        
        logger.info(
            f"FinancialDataProfiler initialized - "
            f"DataProfiler: {self.dataprofiler_available}, "
            f"Pandas: {self.pandas_available}, "
            f"Polars: {self.polars_available}"
        )
    
    def profile_financial_data(self, 
                              data: Union[str, pd.DataFrame, pl.DataFrame, List[Dict]],
                              data_type: str = 'auto') -> Dict[str, Any]:
        """Profile financial data for schema, statistics, and sensitive information.
        
        Args:
            data: Financial data to profile (file path, DataFrame, or list of dicts)
            data_type: Type of data ('csv', 'json', 'dataframe', 'auto')
            
        Returns:
            Dictionary containing profiling results
        """
        if not self.dataprofiler_available:
            return self._fallback_profile(data)
        
        try:
            # Convert data to format suitable for DataProfiler
            profile_data = self._prepare_data_for_profiling(data, data_type)
            
            # Create and run DataProfiler
            profile = dp.ProfilerOptions()
            profile.set({
                "data_labeler.is_enabled": True,  # Enable sensitive data detection
                "correlation.is_enabled": True,   # Enable correlation analysis
                "chi2_homogeneity.is_enabled": True,  # Enable statistical tests
            })
            
            profiler = dp.Profiler(profile_data, options=profile)
            report = profiler.report()
            
            # Extract and organize results
            results = self._extract_profiling_results(report)
            
            # Add financial-specific analysis
            results.update(self._analyze_financial_patterns(profile_data))
            
            return results
        
        except Exception as e:
            logger.error(f"DataProfiler error: {e}")
            return self._fallback_profile(data)
    
    def _prepare_data_for_profiling(self, 
                                   data: Union[str, pd.DataFrame, pl.DataFrame, List[Dict]],
                                   data_type: str) -> pd.DataFrame:
        """Convert input data to DataFrame for DataProfiler."""
        if isinstance(data, str):
            # File path - let DataProfiler handle it
            return data
        elif isinstance(data, pd.DataFrame):
            return data
        elif self.polars_available and isinstance(data, pl.DataFrame):
            # Convert Polars to Pandas for DataProfiler
            return data.to_pandas()
        elif isinstance(data, list):
            # List of dictionaries to DataFrame
            if self.pandas_available:
                return pd.DataFrame(data)
            else:
                raise ValueError("Pandas required for list-to-DataFrame conversion")
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
    
    def _extract_profiling_results(self, report: Dict) -> Dict[str, Any]:
        """Extract relevant results from DataProfiler report."""
        results = {
            'timestamp': datetime.now().isoformat(),
            'data_stats': {},
            'column_profiles': {},
            'sensitive_data_alerts': [],
            'data_quality_issues': [],
            'recommendations': [],
        }
        
        try:
            # Extract global data statistics
            if 'global_stats' in report:
                global_stats = report['global_stats']
                results['data_stats'] = {
                    'row_count': global_stats.get('samples_used', 0),
                    'column_count': global_stats.get('column_count', 0),
                    'memory_size': global_stats.get('memory_size', 0),
                    'null_ratio': global_stats.get('null_ratio', 0),
                }
            
            # Extract column-level profiles
            if 'data_stats' in report:
                for column_name, column_stats in report['data_stats'].items():
                    if isinstance(column_stats, dict):
                        results['column_profiles'][column_name] = {
                            'data_type': column_stats.get('data_type', 'unknown'),
                            'null_count': column_stats.get('null_count', 0),
                            'unique_count': column_stats.get('unique_count', 0),
                            'statistics': column_stats.get('statistics', {}),
                            'data_label': column_stats.get('data_label', 'unknown'),
                        }
                        
                        # Check for sensitive data labels
                        data_label = column_stats.get('data_label', '').lower()
                        if any(sensitive in data_label for sensitive in 
                               ['ssn', 'credit_card', 'phone', 'email', 'address']):
                            results['sensitive_data_alerts'].append({
                                'column': column_name,
                                'data_label': data_label,
                                'severity': 'high',
                                'recommendation': f'Consider encrypting or masking {column_name}'
                            })
            
            # Extract data quality issues
            results['data_quality_issues'] = self._identify_data_quality_issues(
                results['column_profiles']
            )
            
            # Generate recommendations
            results['recommendations'] = self._generate_recommendations(
                results['column_profiles'], 
                results['sensitive_data_alerts']
            )
        
        except Exception as e:
            logger.error(f"Error extracting profiling results: {e}")
            results['error'] = str(e)
        
        return results
    
    def _analyze_financial_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze financial-specific patterns in the data."""
        financial_analysis = {
            'financial_columns': [],
            'potential_currencies': [],
            'date_columns': [],
            'numeric_precision_issues': [],
        }
        
        if not self.pandas_available or not isinstance(data, pd.DataFrame):
            return financial_analysis
        
        try:
            for column in data.columns:
                col_data = data[column]
                
                # Identify financial columns
                if any(term in column.lower() for term in 
                       ['price', 'amount', 'value', 'cost', 'fee', 'return', 'yield']):
                    financial_analysis['financial_columns'].append({
                        'column': column,
                        'min_value': float(col_data.min()) if col_data.dtype in ['int64', 'float64'] else None,
                        'max_value': float(col_data.max()) if col_data.dtype in ['int64', 'float64'] else None,
                        'has_negatives': bool((col_data < 0).any()) if col_data.dtype in ['int64', 'float64'] else False,
                    })
                
                # Identify currency patterns
                if col_data.dtype == 'object':
                    sample_values = col_data.dropna().head(10).astype(str)
                    if any(any(symbol in val for symbol in ['$', '€', '£', '¥']) 
                           for val in sample_values):
                        financial_analysis['potential_currencies'].append(column)
                
                # Identify date columns
                if 'date' in column.lower() or 'time' in column.lower():
                    financial_analysis['date_columns'].append(column)
                
                # Check for precision issues in financial data
                if col_data.dtype == 'float64' and column in [c['column'] for c in financial_analysis['financial_columns']]:
                    # Check for values that might have floating-point precision issues
                    decimal_places = col_data.apply(lambda x: len(str(x).split('.')[-1]) if '.' in str(x) else 0)
                    if decimal_places.max() > 2:
                        financial_analysis['numeric_precision_issues'].append({
                            'column': column,
                            'max_decimal_places': int(decimal_places.max()),
                            'recommendation': 'Consider using Decimal type for financial precision'
                        })
        
        except Exception as e:
            logger.error(f"Error in financial pattern analysis: {e}")
            financial_analysis['error'] = str(e)
        
        return financial_analysis
    
    def _identify_data_quality_issues(self, column_profiles: Dict) -> List[Dict]:
        """Identify common data quality issues in financial data."""
        issues = []
        
        for column_name, profile in column_profiles.items():
            try:
                # High null ratio
                null_count = profile.get('null_count', 0)
                # Assuming we can derive total count from context
                if null_count > 0:
                    issues.append({
                        'column': column_name,
                        'issue': 'high_null_ratio',
                        'severity': 'medium' if null_count < 100 else 'high',
                        'description': f'Column has {null_count} null values'
                    })
                
                # Low cardinality for non-categorical data
                unique_count = profile.get('unique_count', 0)
                data_type = profile.get('data_type', '')
                
                if data_type in ['int', 'float'] and unique_count < 5:
                    issues.append({
                        'column': column_name,
                        'issue': 'low_cardinality',
                        'severity': 'low',
                        'description': f'Numeric column has only {unique_count} unique values'
                    })
            
            except Exception as e:
                logger.error(f"Error analyzing column {column_name}: {e}")
        
        return issues
    
    def _generate_recommendations(self, 
                                column_profiles: Dict, 
                                sensitive_alerts: List[Dict]) -> List[str]:
        """Generate data handling recommendations."""
        recommendations = []
        
        # Sensitive data recommendations
        if sensitive_alerts:
            recommendations.append(
                "🔒 Sensitive data detected. Implement encryption and access controls."
            )
        
        # Financial precision recommendations
        financial_columns = [col for col in column_profiles 
                           if any(term in col.lower() for term in 
                                 ['price', 'amount', 'value', 'cost'])]
        if financial_columns:
            recommendations.append(
                "💰 Use Decimal type for financial calculations to avoid precision errors."
            )
        
        # Data validation recommendations
        recommendations.append(
            "✅ Implement data validation rules for all financial inputs."
        )
        
        # Performance recommendations
        if len(column_profiles) > 50:
            recommendations.append(
                "⚡ Consider using Polars for better performance with large datasets."
            )
        
        return recommendations
    
    def _fallback_profile(self, data: Any) -> Dict[str, Any]:
        """Provide basic profiling when DataProfiler is not available."""
        logger.warning("Using fallback profiling - DataProfiler not available")
        
        fallback_result = {
            'timestamp': datetime.now().isoformat(),
            'data_stats': {},
            'column_profiles': {},
            'sensitive_data_alerts': [],
            'data_quality_issues': [],
            'recommendations': [
                "Install DataProfiler for advanced data profiling: pip install DataProfiler"
            ],
            'fallback_mode': True,
        }
        
        # Basic analysis if we have pandas/polars
        if isinstance(data, (pd.DataFrame, pl.DataFrame)):
            try:
                if isinstance(data, pl.DataFrame):
                    # Basic Polars analysis
                    fallback_result['data_stats'] = {
                        'row_count': data.height,
                        'column_count': data.width,
                        'columns': data.columns,
                    }
                elif isinstance(data, pd.DataFrame):
                    # Basic Pandas analysis
                    fallback_result['data_stats'] = {
                        'row_count': len(data),
                        'column_count': len(data.columns),
                        'columns': list(data.columns),
                        'dtypes': {col: str(dtype) for col, dtype in data.dtypes.items()},
                    }
            except Exception as e:
                logger.error(f"Fallback profiling error: {e}")
        
        return fallback_result
    
    def profile_portfolio_data(self, portfolio_data: List[Dict]) -> Dict[str, Any]:
        """Specialized profiling for portfolio data."""
        if not portfolio_data:
            return {'error': 'No portfolio data provided'}
        
        # Convert to DataFrame for analysis
        if self.pandas_available:
            df = pd.DataFrame(portfolio_data)
            return self.profile_financial_data(df, 'dataframe')
        else:
            return self._fallback_profile(portfolio_data)
    
    def validate_financial_data_types(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that financial data uses appropriate types."""
        validation_results = {
            'valid': True,
            'issues': [],
            'recommendations': []
        }
        
        financial_fields = ['price', 'amount', 'value', 'cost', 'fee', 'return']
        
        for key, value in data.items():
            if any(field in key.lower() for field in financial_fields):
                if isinstance(value, float):
                    validation_results['issues'].append({
                        'field': key,
                        'issue': 'float_precision',
                        'value': value,
                        'recommendation': 'Use Decimal type for financial precision'
                    })
                    validation_results['valid'] = False
                
                elif isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit():
                    validation_results['recommendations'].append(
                        f"Convert string field '{key}' to appropriate numeric type"
                    )
        
        return validation_results


# Global instance for easy access
financial_profiler = FinancialDataProfiler()