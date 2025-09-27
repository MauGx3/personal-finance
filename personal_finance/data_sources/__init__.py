"""Financial data sources module.

This module provides robust financial data source integrations with
adapter patterns for testability and flexibility.
"""

from .services import (
    DataSourceService,
    create_yfinance_service,
    create_mock_service,
)
from .adapter import YFinanceAdapter, MockAdapter, BaseDataSourceAdapter
from .types import (
    PricePoint,
    HistoricalSeries,
    HistoricalPricePoint,
    CompanyInfo,
)

__all__ = [
    "DataSourceService",
    "create_yfinance_service",
    "create_mock_service",
    "YFinanceAdapter",
    "MockAdapter",
    "BaseDataSourceAdapter",
    "PricePoint",
    "HistoricalSeries",
    "HistoricalPricePoint",
    "CompanyInfo",
]
