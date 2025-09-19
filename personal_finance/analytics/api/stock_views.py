"""API views for stock analysis functionality."""

import logging
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache
from django.conf import settings
from datetime import datetime, timedelta

from ..stock_analysis import StockAnalysisService, MarketDataService

logger = logging.getLogger(__name__)


@api_view(["GET"])
def stock_analysis(request, symbol):
    """Get comprehensive stock analysis for a given symbol.

    Args:
        symbol: Stock symbol to analyze

    Returns:
        Complete stock analysis including financials, technical, and valuation analysis
    """
    try:
        # Check cache first (cache for 1 hour)
        cache_key = f"stock_analysis_{symbol.upper()}"
        cached_result = cache.get(cache_key)

        if cached_result:
            logger.info(f"Returning cached analysis for {symbol}")
            return Response(cached_result)

        # Perform analysis
        analysis_service = StockAnalysisService()
        result = analysis_service.analyze_stock(symbol.upper())

        # Convert to dictionary for JSON response
        response_data = {
            "symbol": result.symbol,
            "analysis_date": result.analysis_date.isoformat(),
            "financials": _serialize_financials(result.financials)
            if result.financials
            else None,
            "technical_indicators": result.technical_indicators,
            "valuation": {
                "fair_value_estimate": result.fair_value_estimate,
                "valuation_score": result.valuation_score,
            },
            "risk_analysis": {
                "beta": result.beta,
                "volatility": result.volatility,
                "var_95": result.var_95,
            },
            "growth_analysis": {
                "revenue_growth": result.revenue_growth,
                "earnings_growth": result.earnings_growth,
            },
            "dividend_analysis": {
                "dividend_yield": result.dividend_yield,
                "dividend_growth_rate": result.dividend_growth_rate,
                "payout_ratio": result.payout_ratio,
            },
            "overall_assessment": {
                "overall_score": result.overall_score,
                "recommendation": result.recommendation,
            },
        }

        # Cache the result
        cache.set(cache_key, response_data, 3600)  # 1 hour

        return Response(response_data)

    except Exception as e:
        logger.error(f"Error analyzing stock {symbol}: {e}")
        return Response(
            {"error": f"Failed to analyze stock {symbol}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def stock_financials(request, symbol):
    """Get detailed financial data for a stock.

    Args:
        symbol: Stock symbol

    Returns:
        Detailed financial statements and ratios
    """
    try:
        cache_key = f"stock_financials_{symbol.upper()}"
        cached_result = cache.get(cache_key)

        if cached_result:
            return Response(cached_result)

        analysis_service = StockAnalysisService()
        financials = analysis_service._get_company_financials(symbol.upper())

        response_data = (
            _serialize_financials(financials) if financials else None
        )

        # Cache for 6 hours (financials change less frequently)
        cache.set(cache_key, response_data, 21600)

        return Response(response_data)

    except Exception as e:
        logger.error(f"Error getting financials for {symbol}: {e}")
        return Response(
            {"error": f"Failed to get financials for {symbol}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def stock_technical_analysis(request, symbol):
    """Get technical analysis for a stock.

    Args:
        symbol: Stock symbol

    Returns:
        Technical indicators and analysis
    """
    try:
        cache_key = f"stock_technical_{symbol.upper()}"
        cached_result = cache.get(cache_key)

        if cached_result:
            return Response(cached_result)

        analysis_service = StockAnalysisService()
        technical_data = analysis_service._perform_technical_analysis(
            symbol.upper()
        )

        # Cache for 15 minutes (technical data changes frequently)
        cache.set(cache_key, technical_data, 900)

        return Response(technical_data)

    except Exception as e:
        logger.error(f"Error getting technical analysis for {symbol}: {e}")
        return Response(
            {"error": f"Failed to get technical analysis for {symbol}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def stock_real_time_quote(request, symbol):
    """Get real-time quote for a stock.

    Args:
        symbol: Stock symbol

    Returns:
        Real-time quote data
    """
    try:
        market_service = MarketDataService()
        quote_data = market_service.get_real_time_quote(symbol.upper())

        return Response(quote_data)

    except Exception as e:
        logger.error(f"Error getting real-time quote for {symbol}: {e}")
        return Response(
            {"error": f"Failed to get quote for {symbol}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def stock_market_sentiment(request, symbol):
    """Get market sentiment data for a stock.

    Args:
        symbol: Stock symbol

    Returns:
        Market sentiment indicators
    """
    try:
        cache_key = f"stock_sentiment_{symbol.upper()}"
        cached_result = cache.get(cache_key)

        if cached_result:
            return Response(cached_result)

        market_service = MarketDataService()
        sentiment_data = market_service.get_market_sentiment(symbol.upper())

        # Cache for 4 hours
        cache.set(cache_key, sentiment_data, 14400)

        return Response(sentiment_data)

    except Exception as e:
        logger.error(f"Error getting market sentiment for {symbol}: {e}")
        return Response(
            {"error": f"Failed to get market sentiment for {symbol}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def stock_sector_comparison(request, symbol):
    """Compare stock with its sector.

    Args:
        symbol: Stock symbol

    Returns:
        Sector comparison data
    """
    try:
        # Get sector from query params or try to determine it
        sector = request.GET.get("sector", "Technology")  # Default sector

        cache_key = f"stock_sector_comparison_{symbol.upper()}_{sector}"
        cached_result = cache.get(cache_key)

        if cached_result:
            return Response(cached_result)

        market_service = MarketDataService()
        comparison_data = market_service.compare_with_sector(
            symbol.upper(), sector
        )

        # Cache for 2 hours
        cache.set(cache_key, comparison_data, 7200)

        return Response(comparison_data)

    except Exception as e:
        logger.error(f"Error getting sector comparison for {symbol}: {e}")
        return Response(
            {"error": f"Failed to get sector comparison for {symbol}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
def compare_stocks(request):
    """Compare multiple stocks.

    Request body should contain:
    {
        "symbols": ["AAPL", "GOOGL", "MSFT"],
        "metrics": ["pe_ratio", "market_cap", "revenue_growth"]  # optional
    }

    Returns:
        Comparison data for the specified stocks
    """
    try:
        symbols = request.data.get("symbols", [])
        metrics = request.data.get(
            "metrics",
            ["pe_ratio", "market_cap", "revenue_growth", "overall_score"],
        )

        if not symbols or len(symbols) < 2:
            return Response(
                {"error": "At least 2 symbols required for comparison"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Limit to 10 stocks to prevent performance issues
        if len(symbols) > 10:
            return Response(
                {"error": "Maximum 10 stocks allowed for comparison"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        analysis_service = StockAnalysisService()
        comparison_data = {
            "symbols": symbols,
            "metrics": metrics,
            "comparison": {},
        }

        # Get analysis for each stock
        for symbol in symbols:
            try:
                result = analysis_service.analyze_stock(symbol.upper())
                stock_data = {
                    "symbol": symbol.upper(),
                    "overall_score": result.overall_score,
                    "recommendation": result.recommendation,
                    "pe_ratio": None,
                    "market_cap": None,
                    "revenue_growth": None,
                }

                # Extract specific financial metrics
                if result.financials and result.financials.financial_ratios:
                    stock_data["pe_ratio"] = (
                        result.financials.financial_ratios.pe_ratio
                    )
                    stock_data["market_cap"] = result.financials.market_cap

                if result.revenue_growth:
                    stock_data["revenue_growth"] = result.revenue_growth.get(
                        "1y"
                    )

                comparison_data["comparison"][symbol.upper()] = stock_data

            except Exception as e:
                logger.error(f"Error analyzing {symbol} for comparison: {e}")
                comparison_data["comparison"][symbol.upper()] = {
                    "symbol": symbol.upper(),
                    "error": f"Failed to analyze {symbol}",
                }

        return Response(comparison_data)

    except Exception as e:
        logger.error(f"Error comparing stocks: {e}")
        return Response(
            {"error": "Failed to compare stocks"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def _serialize_financials(financials):
    """Helper function to serialize financials data for JSON response."""
    if not financials:
        return None

    data = {
        "symbol": financials.symbol,
        "company_name": financials.company_name,
        "income_statement": {
            "revenue": financials.revenue,
            "gross_profit": financials.gross_profit,
            "operating_income": financials.operating_income,
            "net_income": financials.net_income,
            "eps": financials.eps,
        },
        "balance_sheet": {
            "total_assets": financials.total_assets,
            "total_liabilities": financials.total_liabilities,
            "shareholders_equity": financials.shareholders_equity,
            "cash_and_equivalents": financials.cash_and_equivalents,
            "total_debt": financials.total_debt,
        },
        "cash_flow": {
            "operating_cash_flow": financials.operating_cash_flow,
            "free_cash_flow": financials.free_cash_flow,
            "capex": financials.capex,
        },
        "market_data": {
            "market_cap": financials.market_cap,
            "enterprise_value": financials.enterprise_value,
            "shares_outstanding": financials.shares_outstanding,
            "current_price": financials.current_price,
        },
    }

    # Add financial ratios if available
    if financials.financial_ratios:
        data["financial_ratios"] = {
            "profitability": {
                "gross_margin": financials.financial_ratios.gross_margin,
                "operating_margin": financials.financial_ratios.operating_margin,
                "net_margin": financials.financial_ratios.net_margin,
                "roe": financials.financial_ratios.roe,
                "roa": financials.financial_ratios.roa,
                "roic": financials.financial_ratios.roic,
            },
            "liquidity": {
                "current_ratio": financials.financial_ratios.current_ratio,
                "quick_ratio": financials.financial_ratios.quick_ratio,
                "cash_ratio": financials.financial_ratios.cash_ratio,
            },
            "leverage": {
                "debt_to_equity": financials.financial_ratios.debt_to_equity,
                "debt_to_assets": financials.financial_ratios.debt_to_assets,
                "interest_coverage": financials.financial_ratios.interest_coverage,
            },
            "efficiency": {
                "asset_turnover": financials.financial_ratios.asset_turnover,
                "inventory_turnover": financials.financial_ratios.inventory_turnover,
                "receivables_turnover": financials.financial_ratios.receivables_turnover,
            },
            "valuation": {
                "pe_ratio": financials.financial_ratios.pe_ratio,
                "pb_ratio": financials.financial_ratios.pb_ratio,
                "ps_ratio": financials.financial_ratios.ps_ratio,
                "ev_ebitda": financials.financial_ratios.ev_ebitda,
                "peg_ratio": financials.financial_ratios.peg_ratio,
            },
        }

    return data
