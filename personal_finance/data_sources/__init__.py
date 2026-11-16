"""Financial data sources module.

This module provides robust financial data source integrations with
adapter patterns for testability and flexibility.
"""

from .adapter import BaseDataSourceAdapter, MockAdapter, YFinanceAdapter
from .services import (
    DataSourceService,
    create_mock_service,
    create_yfinance_service,
)
from .types import (
    CompanyInfo,
    HistoricalPricePoint,
    HistoricalSeries,
    PricePoint,
)

__all__ = [
    "BaseDataSourceAdapter",
    "CompanyInfo",
    "DataSourceService",
    "HistoricalPricePoint",
    "HistoricalSeries",
    "MockAdapter",
    "PricePoint",
    "YFinanceAdapter",
    "create_mock_service",
    "create_yfinance_service",
]
