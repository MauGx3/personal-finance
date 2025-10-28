"""
YFinance Data Source Implementation

Comprehensive implementation of Yahoo Finance data access
using the yfinance library.
"""

import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

import pandas as pd

try:
    import yfinance as yf

    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    yf = None

from ..base import (
    AnalystRecommendation,
    BaseDataSource,
    CompanyInfo,
    DataSourceError,
    DataSourceType,
    DataUnavailableError,
    FinancialStatement,
    NewsItem,
    PriceData,
)

logger = logging.getLogger(__name__)


class YFinanceDataSource(BaseDataSource):
    """
    Yahoo Finance data source implementation.

    Provides comprehensive access to Yahoo Finance data including:
    - Historical price data
    - Company fundamentals
    - Financial statements
    - News and analysis
    - Options data
    """

    def __init__(self, api_key: str | None = None, timeout: int = 30):
        if not YFINANCE_AVAILABLE:
            raise ImportError(
                "yfinance package is required for YFinanceDataSource. "
                "Install it with: pip install yfinance"
            )
        super().__init__(api_key, timeout)

    @property
    def source_type(self) -> DataSourceType:
        return DataSourceType.STOCK_API

    @property
    def name(self) -> str:
        return "Yahoo Finance"

    @property
    def base_url(self) -> str:
        return "https://finance.yahoo.com"

    def get_price_history(
        self,
        symbol: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        interval: str = "1d",
    ) -> list[PriceData]:
        """
        Get historical price data for a symbol.

        Args:
            symbol: The ticker symbol
            start_date: Start date for data (optional)
            end_date: End date for data (optional)
            interval: Data interval ("1d", "1h", "1m", etc.)

        Returns:
            List of PriceData objects
        """
        try:
            ticker = yf.Ticker(symbol)

            # Set default dates if not provided
            if end_date is None:
                end_date = datetime.now()
            if start_date is None:
                start_date = end_date.replace(year=end_date.year - 1)

            # Download historical data
            hist = ticker.history(
                start=start_date, end=end_date, interval=interval, timeout=self.timeout
            )

            if hist.empty:
                return []

            price_data = []
            for index, row in hist.iterrows():
                try:
                    price_data.append(
                        PriceData(
                            date=index.to_pydatetime(),
                            open=self._to_decimal(row.get("Open")),
                            high=self._to_decimal(row.get("High")),
                            low=self._to_decimal(row.get("Low")),
                            close=self._to_decimal(row.get("Close")),
                            volume=int(row.get("Volume", 0))
                            if pd.notna(row.get("Volume"))
                            else None,
                            adjusted_close=self._to_decimal(row.get("Adj Close")),
                        )
                    )
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error processing price data for {symbol} on {index}: {e}")
                    continue

            return price_data

        except Exception as e:
            logger.error(f"Error fetching price history for {symbol}: {e}")
            raise DataSourceError(f"Failed to fetch price history: {str(e)}") from e

    def get_company_info(self, symbol: str) -> CompanyInfo:
        """
        Get fundamental company information.

        Args:
            symbol: The ticker symbol

        Returns:
            CompanyInfo object
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info:
                raise DataUnavailableError(f"No information available for symbol {symbol}")

            return CompanyInfo(
                symbol=symbol.upper(),
                name=info.get("longName") or info.get("shortName"),
                sector=info.get("sector"),
                industry=info.get("industry"),
                country=info.get("country"),
                market_cap=self._to_decimal(info.get("marketCap")),
                pe_ratio=self._to_decimal(info.get("trailingPE")),
                pb_ratio=self._to_decimal(info.get("priceToBook")),
                dividend_yield=self._to_decimal(info.get("dividendYield")),
                beta=self._to_decimal(info.get("beta")),
                fifty_two_week_high=self._to_decimal(info.get("fiftyTwoWeekHigh")),
                fifty_two_week_low=self._to_decimal(info.get("fiftyTwoWeekLow")),
                average_volume=int(info.get("averageVolume", 0))
                if info.get("averageVolume")
                else None,
                currency=info.get("currency"),
                exchange=info.get("exchange"),
                isin=info.get("isin"),
                cusip=info.get("cusip"),
                sedol=info.get("sedol"),
            )

        except Exception as e:
            logger.error(f"Error fetching company info for {symbol}: {e}")
            raise DataSourceError(f"Failed to fetch company info: {str(e)}") from e

    def get_news(self, symbol: str, limit: int = 10) -> list[NewsItem]:
        """
        Get recent news for a symbol.

        Args:
            symbol: The ticker symbol
            limit: Maximum number of news items to return

        Returns:
            List of NewsItem objects
        """
        try:
            ticker = yf.Ticker(symbol)
            news_data = ticker.news

            if not news_data:
                return []

            news_items = []
            for item in news_data[:limit]:
                try:
                    # Parse the publish time
                    published_at = datetime.fromtimestamp(item.get("providerPublishTime", 0))

                    news_items.append(
                        NewsItem(
                            title=item.get("title", ""),
                            summary=item.get("summary"),
                            url=item.get("link", ""),
                            published_at=published_at,
                            source=item.get("publisher"),
                            author=None,  # Not available in yfinance news
                            tags=None,  # Not available in yfinance news
                        )
                    )
                except (ValueError, TypeError, KeyError) as e:
                    logger.warning(f"Error processing news item for {symbol}: {e}")
                    continue

            return news_items

        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            raise DataSourceError(f"Failed to fetch news: {str(e)}") from e

    def get_analyst_recommendations(self, symbol: str) -> list[AnalystRecommendation]:
        """
        Get analyst recommendations for a symbol.

        Args:
            symbol: The ticker symbol

        Returns:
            List of AnalystRecommendation objects
        """
        try:
            ticker = yf.Ticker(symbol)
            recommendations = ticker.recommendations

            if recommendations is None or recommendations.empty:
                return []

            analyst_recs = []
            for _, row in recommendations.iterrows():
                try:
                    analyst_recs.append(
                        AnalystRecommendation(
                            firm=row.get("Firm", ""),
                            recommendation=row.get("To Grade", ""),
                            target_price=self._to_decimal(row.get("Target Price")),
                            currency=None,  # Not specified in yfinance
                            date=pd.to_datetime(row.get("Date")).to_pydatetime(),
                        )
                    )
                except (ValueError, TypeError, KeyError) as e:
                    logger.warning(f"Error processing analyst recommendation for {symbol}: {e}")
                    continue

            return analyst_recs

        except Exception as e:
            logger.error(f"Error fetching analyst recommendations for {symbol}: {e}")
            raise DataSourceError(f"Failed to fetch analyst recommendations: {str(e)}") from e

    def get_income_statement(
        self, symbol: str, annual: bool = True, limit: int = 4
    ) -> list[FinancialStatement]:
        """
        Get income statement data.

        Args:
            symbol: The ticker symbol
            annual: If True, get annual data; if False, get quarterly
            limit: Number of periods to return

        Returns:
            List of FinancialStatement objects
        """
        try:
            ticker = yf.Ticker(symbol)

            financials = ticker.financials if annual else ticker.quarterly_financials

            if financials is None or financials.empty:
                return []

            statements = []
            for i, col_date in enumerate(financials.columns[:limit]):
                try:
                    period_date = col_date.date() if hasattr(col_date, "date") else col_date

                    statements.append(
                        FinancialStatement(
                            period_end=period_date,
                            revenue=self._to_decimal(
                                financials.loc["Total Revenue", col_date]
                                if "Total Revenue" in financials.index
                                else None
                            ),
                            cost_of_revenue=self._to_decimal(
                                financials.loc["Cost Of Revenue", col_date]
                                if "Cost Of Revenue" in financials.index
                                else None
                            ),
                            gross_profit=self._to_decimal(
                                financials.loc["Gross Profit", col_date]
                                if "Gross Profit" in financials.index
                                else None
                            ),
                            operating_expenses=self._to_decimal(
                                financials.loc["Operating Expenses", col_date]
                                if "Operating Expenses" in financials.index
                                else None
                            ),
                            operating_income=self._to_decimal(
                                financials.loc["Operating Income", col_date]
                                if "Operating Income" in financials.index
                                else None
                            ),
                            net_income=self._to_decimal(
                                financials.loc["Net Income", col_date]
                                if "Net Income" in financials.index
                                else None
                            ),
                            eps=self._to_decimal(
                                financials.loc["Diluted EPS", col_date]
                                if "Diluted EPS" in financials.index
                                else None
                            ),
                            diluted_eps=self._to_decimal(
                                financials.loc["Diluted EPS", col_date]
                                if "Diluted EPS" in financials.index
                                else None
                            ),
                        )
                    )
                except (ValueError, TypeError, KeyError) as e:
                    logger.warning(
                        f"Error processing income statement for {symbol} period {i}: {e}"
                    )
                    continue

            return statements

        except Exception as e:
            logger.error(f"Error fetching income statement for {symbol}: {e}")
            raise DataSourceError(f"Failed to fetch income statement: {str(e)}") from e

    def get_balance_sheet(
        self, symbol: str, annual: bool = True, limit: int = 4
    ) -> list[dict[str, Any]]:
        """
        Get balance sheet data.

        Args:
            symbol: The ticker symbol
            annual: If True, get annual data; if False, get quarterly
            limit: Number of periods to return

        Returns:
            List of dictionaries containing balance sheet data
        """
        try:
            ticker = yf.Ticker(symbol)

            balance_sheet = ticker.balance_sheet if annual else ticker.quarterly_balance_sheet

            if balance_sheet is None or balance_sheet.empty:
                return []

            balance_sheets = []
            for col_date in balance_sheet.columns[:limit]:
                try:
                    period_date = col_date.date() if hasattr(col_date, "date") else col_date
                    sheet_data = {
                        "period_end": period_date,
                    }

                    # Add all available balance sheet items
                    for index in balance_sheet.index:
                        value = balance_sheet.loc[index, col_date]
                        sheet_data[index] = self._to_decimal(value)

                    balance_sheets.append(sheet_data)
                except (ValueError, TypeError, KeyError) as e:
                    logger.warning(f"Error processing balance sheet for {symbol}: {e}")
                    continue

            return balance_sheets

        except Exception as e:
            logger.error(f"Error fetching balance sheet for {symbol}: {e}")
            raise DataSourceError(f"Failed to fetch balance sheet: {str(e)}") from e

    def get_cash_flow(
        self, symbol: str, annual: bool = True, limit: int = 4
    ) -> list[dict[str, Any]]:
        """
        Get cash flow statement data.

        Args:
            symbol: The ticker symbol
            annual: If True, get annual data; if False, get quarterly
            limit: Number of periods to return

        Returns:
            List of dictionaries containing cash flow data
        """
        try:
            ticker = yf.Ticker(symbol)

            cash_flow = ticker.cashflow if annual else ticker.quarterly_cashflow

            if cash_flow is None or cash_flow.empty:
                return []

            cash_flows = []
            for col_date in cash_flow.columns[:limit]:
                try:
                    period_date = col_date.date() if hasattr(col_date, "date") else col_date
                    flow_data = {
                        "period_end": period_date,
                    }

                    # Add all available cash flow items
                    for index in cash_flow.index:
                        value = cash_flow.loc[index, col_date]
                        flow_data[index] = self._to_decimal(value)

                    cash_flows.append(flow_data)
                except (ValueError, TypeError, KeyError) as e:
                    logger.warning(f"Error processing cash flow for {symbol}: {e}")
                    continue

            return cash_flows

        except Exception as e:
            logger.error(f"Error fetching cash flow for {symbol}: {e}")
            raise DataSourceError(f"Failed to fetch cash flow: {str(e)}") from e

    def get_dividends(self, symbol: str) -> list[dict[str, Any]]:
        """
        Get dividend history for a symbol.

        Args:
            symbol: The ticker symbol

        Returns:
            List of dictionaries with dividend data
        """
        try:
            ticker = yf.Ticker(symbol)
            dividends = ticker.dividends

            if dividends is None or dividends.empty:
                return []

            dividend_data = []
            for date_idx, amount in dividends.items():
                try:
                    dividend_data.append(
                        {
                            "date": date_idx.date() if hasattr(date_idx, "date") else date_idx,
                            "amount": self._to_decimal(amount),
                            "currency": None,  # Not specified in yfinance
                        }
                    )
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error processing dividend for {symbol}: {e}")
                    continue

            return dividend_data

        except Exception as e:
            logger.error(f"Error fetching dividends for {symbol}: {e}")
            raise DataSourceError(f"Failed to fetch dividends: {str(e)}") from e

    def get_splits(self, symbol: str) -> list[dict[str, Any]]:
        """
        Get stock split history for a symbol.

        Args:
            symbol: The ticker symbol

        Returns:
            List of dictionaries with split data
        """
        try:
            ticker = yf.Ticker(symbol)
            splits = ticker.splits

            if splits is None or splits.empty:
                return []

            split_data = []
            for date_idx, ratio in splits.items():
                try:
                    split_data.append(
                        {
                            "date": date_idx.date() if hasattr(date_idx, "date") else date_idx,
                            "ratio": float(ratio),
                        }
                    )
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error processing split for {symbol}: {e}")
                    continue

            return split_data

        except Exception as e:
            logger.error(f"Error fetching splits for {symbol}: {e}")
            raise DataSourceError(f"Failed to fetch splits: {str(e)}") from e

    def get_options_chain(self, symbol: str) -> dict[str, Any]:
        """
        Get options chain data for a symbol.

        Args:
            symbol: The ticker symbol

        Returns:
            Dictionary containing options data
        """
        try:
            ticker = yf.Ticker(symbol)
            options = ticker.options

            if not options:
                return {}

            options_data = {
                "expiration_dates": options,
                "chains": {},
            }

            # Get options chain for the first expiration date
            if options:
                try:
                    chain = ticker.option_chain(options[0])
                    options_data["chains"][options[0]] = {
                        "calls": chain.calls.to_dict("records")
                        if hasattr(chain.calls, "to_dict")
                        else [],
                        "puts": chain.puts.to_dict("records")
                        if hasattr(chain.puts, "to_dict")
                        else [],
                    }
                except Exception as e:
                    logger.warning(f"Error fetching options chain for {symbol}: {e}")

            return options_data

        except Exception as e:
            logger.error(f"Error fetching options chain for {symbol}: {e}")
            raise DataSourceError(f"Failed to fetch options chain: {str(e)}") from e

    def search_symbols(self, query: str) -> list[dict[str, Any]]:
        """
        Search for symbols matching a query.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of dictionaries with symbol information
        """
        try:
            # yfinance doesn't have a direct search API, so we'll return empty list
            # This could be extended to use other search APIs if needed
            logger.info(f"Symbol search not implemented for yfinance. Query: {query}")
            return []

        except Exception as e:
            logger.error(f"Error searching symbols with query '{query}': {e}")
            raise DataSourceError(f"Failed to search symbols: {str(e)}") from e

    def _to_decimal(self, value: Any) -> Decimal | None:
        """
        Convert a value to Decimal, handling various input types.

        Args:
            value: Value to convert

        Returns:
            Decimal value or None if conversion fails
        """
        if value is None or pd.isna(value):
            return None

        try:
            if isinstance(value, int | float):
                return Decimal(str(value))
            elif isinstance(value, str):
                return Decimal(value)
            else:
                return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return None
