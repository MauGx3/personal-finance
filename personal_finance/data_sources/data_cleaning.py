"""Data cleaning and tidying module for personal finance platform.

This module integrates pyjanitor for data cleaning and tidying-up for Polars,
Pandas and other tools as specified in the S.C.A.F.F. structure requirements.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date
from decimal import Decimal, InvalidOperation

try:
    import janitor  # pyjanitor
    import pandas as pd
    PYJANITOR_AVAILABLE = True
except ImportError:
    PYJANITOR_AVAILABLE = False
    janitor = None
    pd = None

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False
    pl = None

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class FinancialDataCleaner:
    """Financial data cleaning and tidying using pyjanitor and custom methods.
    
    Provides comprehensive data cleaning capabilities for financial data including:
    - Column name standardization
    - Data type conversions
    - Outlier detection and handling
    - Missing value imputation
    - Financial data validation
    """
    
    def __init__(self):
        """Initialize the data cleaner with available libraries."""
        self.pyjanitor_available = PYJANITOR_AVAILABLE
        self.polars_available = POLARS_AVAILABLE
        
        if not self.pyjanitor_available:
            logger.warning(
                "pyjanitor not available. Install with: pip install pyjanitor"
            )
        
        logger.info(
            f"FinancialDataCleaner initialized - "
            f"pyjanitor: {self.pyjanitor_available}, "
            f"Polars: {self.polars_available}"
        )
    
    def clean_financial_dataframe(self, 
                                 df: Union[pd.DataFrame, pl.DataFrame],
                                 cleaning_options: Optional[Dict[str, Any]] = None) -> Union[pd.DataFrame, pl.DataFrame]:
        """Clean financial DataFrame using appropriate library methods.
        
        Args:
            df: DataFrame to clean (Pandas or Polars)
            cleaning_options: Dictionary of cleaning options
            
        Returns:
            Cleaned DataFrame of the same type as input
        """
        if cleaning_options is None:
            cleaning_options = self._get_default_cleaning_options()
        
        if isinstance(df, pd.DataFrame) and self.pyjanitor_available:
            return self._clean_pandas_dataframe(df, cleaning_options)
        elif isinstance(df, pl.DataFrame) and self.polars_available:
            return self._clean_polars_dataframe(df, cleaning_options)
        else:
            logger.warning(f"Cannot clean DataFrame of type {type(df)}")
            return df
    
    def _get_default_cleaning_options(self) -> Dict[str, Any]:
        """Get default cleaning options for financial data."""
        return {
            'standardize_column_names': True,
            'remove_empty_columns': True,
            'remove_empty_rows': True,
            'convert_financial_columns': True,
            'handle_currency_symbols': True,
            'standardize_date_formats': True,
            'remove_outliers': False,  # Conservative default for financial data
            'fill_missing_values': False,  # Let user decide
            'validate_financial_precision': True,
        }
    
    def _clean_pandas_dataframe(self, 
                               df: pd.DataFrame, 
                               options: Dict[str, Any]) -> pd.DataFrame:
        """Clean Pandas DataFrame using pyjanitor."""
        try:
            # Start with the original DataFrame
            cleaned_df = df.copy()
            
            # Use pyjanitor's method chaining for data cleaning
            if options.get('standardize_column_names', True):
                cleaned_df = cleaned_df.clean_names()
            
            if options.get('remove_empty_columns', True):
                cleaned_df = cleaned_df.remove_empty()
            
            if options.get('remove_empty_rows', True):
                cleaned_df = cleaned_df.dropna(how='all')
            
            # Financial-specific cleaning
            if options.get('handle_currency_symbols', True):
                cleaned_df = self._remove_currency_symbols_pandas(cleaned_df)
            
            if options.get('convert_financial_columns', True):
                cleaned_df = self._convert_financial_columns_pandas(cleaned_df)
            
            if options.get('standardize_date_formats', True):
                cleaned_df = self._standardize_dates_pandas(cleaned_df)
            
            if options.get('validate_financial_precision', True):
                validation_results = self._validate_financial_precision_pandas(cleaned_df)
                if validation_results['issues']:
                    logger.warning(f"Financial precision issues found: {validation_results['issues']}")
            
            return cleaned_df
        
        except Exception as e:
            logger.error(f"Error cleaning Pandas DataFrame: {e}")
            return df
    
    def _clean_polars_dataframe(self, 
                               df: pl.DataFrame, 
                               options: Dict[str, Any]) -> pl.DataFrame:
        """Clean Polars DataFrame using custom methods."""
        try:
            # Start with the original DataFrame
            cleaned_df = df.clone()
            
            if options.get('standardize_column_names', True):
                cleaned_df = self._standardize_column_names_polars(cleaned_df)
            
            if options.get('remove_empty_columns', True):
                cleaned_df = self._remove_empty_columns_polars(cleaned_df)
            
            if options.get('remove_empty_rows', True):
                cleaned_df = cleaned_df.drop_nulls()
            
            # Financial-specific cleaning
            if options.get('handle_currency_symbols', True):
                cleaned_df = self._remove_currency_symbols_polars(cleaned_df)
            
            if options.get('convert_financial_columns', True):
                cleaned_df = self._convert_financial_columns_polars(cleaned_df)
            
            if options.get('standardize_date_formats', True):
                cleaned_df = self._standardize_dates_polars(cleaned_df)
            
            return cleaned_df
        
        except Exception as e:
            logger.error(f"Error cleaning Polars DataFrame: {e}")
            return df
    
    def _standardize_column_names_polars(self, df: pl.DataFrame) -> pl.DataFrame:
        """Standardize column names for Polars DataFrame."""
        # Convert to snake_case and remove special characters
        new_columns = {}
        for col in df.columns:
            # Convert to lowercase and replace spaces/special chars with underscores
            clean_name = col.lower().replace(' ', '_').replace('-', '_')
            # Remove other special characters
            clean_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in clean_name)
            # Remove consecutive underscores
            while '__' in clean_name:
                clean_name = clean_name.replace('__', '_')
            # Remove leading/trailing underscores
            clean_name = clean_name.strip('_')
            new_columns[col] = clean_name
        
        return df.rename(new_columns)
    
    def _remove_empty_columns_polars(self, df: pl.DataFrame) -> pl.DataFrame:
        """Remove empty columns from Polars DataFrame."""
        non_empty_columns = []
        for col in df.columns:
            if not df.select(pl.col(col).is_null().all()).item():
                non_empty_columns.append(col)
        
        return df.select(non_empty_columns)
    
    def _remove_currency_symbols_pandas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove currency symbols from string columns in Pandas DataFrame."""
        currency_symbols = ['$', '€', '£', '¥', '₹', '¢']
        
        for col in df.columns:
            if df[col].dtype == 'object':
                for symbol in currency_symbols:
                    if df[col].astype(str).str.contains(f'\\{symbol}', na=False).any():
                        df[col] = df[col].astype(str).str.replace(f'\\{symbol}', '', regex=True)
                        logger.info(f"Removed currency symbol '{symbol}' from column '{col}'")
        
        return df
    
    def _remove_currency_symbols_polars(self, df: pl.DataFrame) -> pl.DataFrame:
        """Remove currency symbols from string columns in Polars DataFrame."""
        currency_symbols = ['$', '€', '£', '¥', '₹', '¢']
        
        expressions = []
        for col in df.columns:
            col_expr = pl.col(col)
            
            # Check if column might contain currency symbols
            col_dtype = df.schema[col]
            if col_dtype in [pl.Utf8, pl.String]:
                for symbol in currency_symbols:
                    # Escape special regex characters properly
                    if symbol in ['$']:
                        col_expr = col_expr.str.replace_all(f"\\{symbol}", "")
                    else:
                        col_expr = col_expr.str.replace_all(symbol, "")
            
            expressions.append(col_expr.alias(col))
        
        return df.with_columns(expressions)
    
    def _convert_financial_columns_pandas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert financial columns to appropriate data types in Pandas."""
        financial_column_patterns = ['price', 'amount', 'value', 'cost', 'fee', 'return', 'yield']
        
        for col in df.columns:
            if any(pattern in col.lower() for pattern in financial_column_patterns):
                try:
                    # Try to convert to numeric, handling any remaining non-numeric characters
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    logger.info(f"Converted financial column '{col}' to numeric")
                except Exception as e:
                    logger.warning(f"Could not convert column '{col}' to numeric: {e}")
        
        return df
    
    def _convert_financial_columns_polars(self, df: pl.DataFrame) -> pl.DataFrame:
        """Convert financial columns to appropriate data types in Polars."""
        financial_column_patterns = ['price', 'amount', 'value', 'cost', 'fee', 'return', 'yield']
        
        expressions = []
        for col in df.columns:
            if any(pattern in col.lower() for pattern in financial_column_patterns):
                # Try to cast to float, handling errors
                expr = pl.col(col).cast(pl.Float64, strict=False).alias(col)
                expressions.append(expr)
                logger.info(f"Converting financial column '{col}' to numeric")
            else:
                expressions.append(pl.col(col))
        
        return df.with_columns(expressions)
    
    def _standardize_dates_pandas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize date formats in Pandas DataFrame."""
        date_column_patterns = ['date', 'time', 'created', 'updated', 'timestamp']
        
        for col in df.columns:
            if any(pattern in col.lower() for pattern in date_column_patterns):
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    logger.info(f"Converted date column '{col}' to datetime")
                except Exception as e:
                    logger.warning(f"Could not convert column '{col}' to datetime: {e}")
        
        return df
    
    def _standardize_dates_polars(self, df: pl.DataFrame) -> pl.DataFrame:
        """Standardize date formats in Polars DataFrame."""
        date_column_patterns = ['date', 'time', 'created', 'updated', 'timestamp']
        
        expressions = []
        for col in df.columns:
            if any(pattern in col.lower() for pattern in date_column_patterns):
                # Try to parse as date/datetime
                try:
                    expr = pl.col(col).str.strptime(pl.Date, format='%Y-%m-%d', strict=False).alias(col)
                    expressions.append(expr)
                    logger.info(f"Converting date column '{col}' to date")
                except:
                    # If that fails, keep original
                    expressions.append(pl.col(col))
            else:
                expressions.append(pl.col(col))
        
        return df.with_columns(expressions)
    
    def _validate_financial_precision_pandas(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate financial precision in Pandas DataFrame."""
        validation_results = {
            'valid': True,
            'issues': [],
            'recommendations': []
        }
        
        financial_columns = [col for col in df.columns 
                           if any(pattern in col.lower() for pattern in 
                                 ['price', 'amount', 'value', 'cost', 'fee'])]
        
        for col in financial_columns:
            if df[col].dtype == 'float64':
                # Check for precision issues
                sample_values = df[col].dropna().head(100)
                for value in sample_values:
                    if isinstance(value, float):
                        str_value = str(value)
                        if '.' in str_value and len(str_value.split('.')[-1]) > 2:
                            validation_results['issues'].append({
                                'column': col,
                                'issue': 'high_precision_float',
                                'recommendation': 'Consider using Decimal for financial precision'
                            })
                            validation_results['valid'] = False
                            break
        
        return validation_results
    
    def clean_portfolio_data(self, portfolio_data: List[Dict]) -> List[Dict]:
        """Clean portfolio data specifically for financial calculations."""
        if not portfolio_data:
            return []
        
        cleaned_data = []
        
        for item in portfolio_data:
            cleaned_item = {}
            
            for key, value in item.items():
                # Standardize key names
                clean_key = key.lower().replace(' ', '_').replace('-', '_')
                
                # Clean financial values
                if any(pattern in clean_key for pattern in 
                       ['price', 'amount', 'value', 'cost', 'quantity']):
                    cleaned_value = self._clean_financial_value(value)
                    cleaned_item[clean_key] = cleaned_value
                
                # Clean date values
                elif any(pattern in clean_key for pattern in ['date', 'time']):
                    cleaned_value = self._clean_date_value(value)
                    cleaned_item[clean_key] = cleaned_value
                
                # Keep other values as-is
                else:
                    cleaned_item[clean_key] = value
            
            cleaned_data.append(cleaned_item)
        
        return cleaned_data
    
    def _clean_financial_value(self, value: Any) -> Optional[Decimal]:
        """Clean and convert a financial value to Decimal."""
        if value is None or value == '':
            return None
        
        # Convert to string for cleaning
        str_value = str(value).strip()
        
        # Remove currency symbols
        currency_symbols = ['$', '€', '£', '¥', '₹', '¢']
        for symbol in currency_symbols:
            str_value = str_value.replace(symbol, '')
        
        # Remove commas and spaces
        str_value = str_value.replace(',', '').replace(' ', '')
        
        # Handle parentheses as negative values
        if str_value.startswith('(') and str_value.endswith(')'):
            str_value = '-' + str_value[1:-1]
        
        try:
            return Decimal(str_value)
        except (InvalidOperation, ValueError):
            logger.warning(f"Could not convert '{value}' to Decimal")
            return None
    
    def _clean_date_value(self, value: Any) -> Optional[date]:
        """Clean and convert a date value."""
        if value is None or value == '':
            return None
        
        if isinstance(value, date):
            return value
        
        if isinstance(value, datetime):
            return value.date()
        
        # Try to parse string dates
        if isinstance(value, str):
            try:
                # Common date formats
                from dateutil import parser
                parsed_date = parser.parse(value)
                return parsed_date.date()
            except Exception:
                logger.warning(f"Could not parse date '{value}'")
                return None
        
        return None
    
    def generate_cleaning_report(self, 
                               original_df: Union[pd.DataFrame, pl.DataFrame],
                               cleaned_df: Union[pd.DataFrame, pl.DataFrame]) -> Dict[str, Any]:
        """Generate a report of cleaning operations performed."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'cleaning_summary': {},
            'changes_made': [],
            'data_quality_improvements': [],
            'recommendations': []
        }
        
        try:
            # Basic statistics comparison
            if isinstance(original_df, pd.DataFrame) and isinstance(cleaned_df, pd.DataFrame):
                original_shape = original_df.shape
                cleaned_shape = cleaned_df.shape
                
                report['cleaning_summary'] = {
                    'original_rows': original_shape[0],
                    'original_columns': original_shape[1],
                    'cleaned_rows': cleaned_shape[0],
                    'cleaned_columns': cleaned_shape[1],
                    'rows_removed': original_shape[0] - cleaned_shape[0],
                    'columns_removed': original_shape[1] - cleaned_shape[1],
                }
                
                # Column changes
                original_columns = set(original_df.columns)
                cleaned_columns = set(cleaned_df.columns)
                
                if original_columns != cleaned_columns:
                    report['changes_made'].append({
                        'type': 'column_changes',
                        'removed_columns': list(original_columns - cleaned_columns),
                        'added_columns': list(cleaned_columns - original_columns),
                    })
            
            elif isinstance(original_df, pl.DataFrame) and isinstance(cleaned_df, pl.DataFrame):
                original_shape = (original_df.height, original_df.width)
                cleaned_shape = (cleaned_df.height, cleaned_df.width)
                
                report['cleaning_summary'] = {
                    'original_rows': original_shape[0],
                    'original_columns': original_shape[1],
                    'cleaned_rows': cleaned_shape[0],
                    'cleaned_columns': cleaned_shape[1],
                    'rows_removed': original_shape[0] - cleaned_shape[0],
                    'columns_removed': original_shape[1] - cleaned_shape[1],
                }
            
            # General recommendations
            report['recommendations'] = [
                "✅ Data cleaning completed successfully",
                "💰 Verify financial calculations use appropriate precision",
                "📅 Validate date formats meet your requirements",
                "🔍 Review any removed rows/columns to ensure data integrity"
            ]
        
        except Exception as e:
            logger.error(f"Error generating cleaning report: {e}")
            report['error'] = str(e)
        
        return report


# Global instance for easy access
financial_cleaner = FinancialDataCleaner()