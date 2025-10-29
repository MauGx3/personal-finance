"""
Data Sources Package

This package provides a modular framework for financial data sources,
allowing easy integration of various financial data providers.
"""

from .base import (
    AnalystRecommendation,
    AuthenticationError,
    BaseDataSource,
    CachingDataSourceMixin,
    CompanyInfo,
    DataSourceError,
    DataSourceType,
    DataUnavailableError,
    FinancialStatement,
    NewsItem,
    PriceData,
    RateLimitedDataSourceMixin,
    RateLimitError,
)
from .yfinance import YFinanceDataSource

__all__ = [
    "BaseDataSource",
    "CachingDataSourceMixin",
    "RateLimitedDataSourceMixin",
    "DataSourceError",
    "RateLimitError",
    "AuthenticationError",
    "DataUnavailableError",
    "DataSourceType",
    "PriceData",
    "CompanyInfo",
    "NewsItem",
    "AnalystRecommendation",
    "FinancialStatement",
    "YFinanceDataSource",
]
