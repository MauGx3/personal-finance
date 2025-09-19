#!/usr/bin/env python3
"""Demo script for stock analysis functionality.

This script demonstrates the stock analysis features including:
- Financial analysis
- Technical indicators
- Market data integration
"""

import sys
import os
from datetime import datetime, timedelta
import json

# Add the project root to the Python path
sys.path.insert(0, "/home/runner/work/personal-finance/personal-finance")


def demo_stock_analysis():
    """Demonstrate stock analysis functionality."""
    print("=== Personal Finance Stock Analysis Demo ===\n")

    try:
        # Import the stock analysis module
        from personal_finance.analytics.stock_analysis import (
            StockAnalysisService,
            MarketDataService,
            CompanyFinancials,
            FinancialRatios,
        )

        print("✓ Stock analysis modules imported successfully\n")

        # Initialize services
        analysis_service = StockAnalysisService()
        market_service = MarketDataService()

        print("✓ Services initialized\n")

        # Demo 1: Basic Stock Analysis
        print("--- Demo 1: Basic Stock Analysis ---")
        symbol = "AAPL"
        print(f"Analyzing stock: {symbol}")

        result = analysis_service.analyze_stock(symbol)

        print(f"Analysis completed for {result.symbol}")
        print(f"Analysis date: {result.analysis_date}")
        print(f"Overall score: {result.overall_score}")
        print(f"Recommendation: {result.recommendation}")
        print(f"Valuation: {result.valuation_score}")
        print()

        # Demo 2: Financial Ratios
        print("--- Demo 2: Financial Ratios Calculation ---")
        sample_financials = CompanyFinancials(
            symbol="DEMO",
            company_name="Demo Company",
            revenue=1000000000.0,  # $1B revenue
            gross_profit=400000000.0,  # 40% gross margin
            operating_income=200000000.0,  # 20% operating margin
            net_income=150000000.0,  # 15% net margin
            total_assets=2000000000.0,  # $2B assets
            shareholders_equity=800000000.0,  # $800M equity
            eps=5.0,  # $5 EPS
            current_price=100.0,  # $100 stock price
            market_cap=5000000000.0,  # $5B market cap
        )

        ratios = analysis_service._calculate_financial_ratios(
            sample_financials
        )

        print("Sample Financial Ratios:")
        print(
            f"  Gross Margin: {ratios.gross_margin:.1%}"
            if ratios.gross_margin
            else "  Gross Margin: N/A"
        )
        print(
            f"  Operating Margin: {ratios.operating_margin:.1%}"
            if ratios.operating_margin
            else "  Operating Margin: N/A"
        )
        print(
            f"  Net Margin: {ratios.net_margin:.1%}"
            if ratios.net_margin
            else "  Net Margin: N/A"
        )
        print(f"  ROE: {ratios.roe:.1%}" if ratios.roe else "  ROE: N/A")
        print(f"  ROA: {ratios.roa:.1%}" if ratios.roa else "  ROA: N/A")
        print(
            f"  P/E Ratio: {ratios.pe_ratio:.1f}"
            if ratios.pe_ratio
            else "  P/E Ratio: N/A"
        )
        print()

        # Demo 3: Technical Indicators
        print("--- Demo 3: Technical Indicators ---")
        try:
            import pandas as pd
            import numpy as np
            from personal_finance.analytics.services import TechnicalIndicators

            # Create sample price data
            dates = pd.date_range("2024-01-01", periods=50, freq="D")
            sample_prices = pd.Series(
                np.random.uniform(95, 105, 50), index=dates
            )
            sample_high = sample_prices + np.random.uniform(1, 3, 50)
            sample_low = sample_prices - np.random.uniform(1, 3, 50)
            sample_volume = pd.Series(
                np.random.randint(1000000, 5000000, 50), index=dates
            )

            print("Calculating technical indicators for sample data...")

            # Moving averages
            sma_20 = TechnicalIndicators.moving_average(sample_prices, 20)
            print(f"  20-day SMA (last value): ${sma_20.iloc[-1]:.2f}")

            # RSI
            rsi = TechnicalIndicators.rsi(sample_prices)
            print(f"  RSI (last value): {rsi.iloc[-1]:.1f}")

            # MACD
            macd_data = TechnicalIndicators.macd(sample_prices)
            print(f"  MACD (last value): {macd_data['macd'].iloc[-1]:.3f}")

            # Bollinger Bands
            bb_data = TechnicalIndicators.bollinger_bands(sample_prices)
            print(
                f"  Bollinger Upper (last): ${bb_data['upper'].iloc[-1]:.2f}"
            )
            print(
                f"  Bollinger Lower (last): ${bb_data['lower'].iloc[-1]:.2f}"
            )

            # Stochastic Oscillator
            stoch_data = TechnicalIndicators.stochastic_oscillator(
                sample_high, sample_low, sample_prices
            )
            print(f"  Stochastic %K (last): {stoch_data['%K'].iloc[-1]:.1f}")

            # Williams %R
            williams_r = TechnicalIndicators.williams_r(
                sample_high, sample_low, sample_prices
            )
            print(f"  Williams %R (last): {williams_r.iloc[-1]:.1f}")

            print()

        except ImportError:
            print(
                "pandas/numpy not available - skipping technical indicators demo\n"
            )

        # Demo 4: Market Data Service
        print("--- Demo 4: Market Data Service ---")

        # Real-time quote (placeholder)
        quote = market_service.get_real_time_quote("AAPL")
        print("Real-time quote structure:")
        for key, value in quote.items():
            print(f"  {key}: {value}")
        print()

        # Market sentiment (placeholder)
        sentiment = market_service.get_market_sentiment("AAPL")
        print("Market sentiment structure:")
        print(f"  Analyst ratings: {sentiment.get('analyst_ratings', {})}")
        print(f"  Price targets: {sentiment.get('price_targets', {})}")
        print()

        # Demo 5: API Structure Preview
        print("--- Demo 5: API Endpoints Structure ---")

        api_endpoints = [
            "/api/stock/AAPL/analysis/",
            "/api/stock/AAPL/financials/",
            "/api/stock/AAPL/technical/",
            "/api/stock/AAPL/quote/",
            "/api/stock/AAPL/sentiment/",
            "/api/stock/AAPL/sector-comparison/",
            "/api/stocks/compare/",
        ]

        print("Available API endpoints:")
        for endpoint in api_endpoints:
            print(f"  {endpoint}")
        print()

        print("✓ Demo completed successfully!")
        print("\nKey Features Implemented:")
        print("  ✓ Comprehensive stock analysis framework")
        print("  ✓ Financial ratios calculation (15+ ratios)")
        print("  ✓ Extended technical indicators (10+ indicators)")
        print("  ✓ Market data integration structure")
        print("  ✓ RESTful API endpoints")
        print("  ✓ Caching and performance optimization")
        print("  ✓ Valuation and risk analysis")
        print("  ✓ Investment recommendation system")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(
            "Some dependencies are not available, but the basic structure is implemented."
        )

    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback

        traceback.print_exc()


def demo_technical_indicators_without_pandas():
    """Demonstrate basic technical analysis concepts without pandas."""
    print("\n--- Basic Technical Analysis Concepts ---")

    # Simple moving average calculation
    prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109]
    window = 5

    sma_values = []
    for i in range(window - 1, len(prices)):
        sma = sum(prices[i - window + 1 : i + 1]) / window
        sma_values.append(sma)

    print(f"Sample prices: {prices}")
    print(f"5-period SMA: {[round(x, 2) for x in sma_values]}")

    # Simple RSI calculation concept
    gains = []
    losses = []

    for i in range(1, len(prices)):
        change = prices[i] - prices[i - 1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))

    avg_gain = sum(gains[-5:]) / 5  # Last 5 periods
    avg_loss = sum(losses[-5:]) / 5

    if avg_loss != 0:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        print(f"Simple RSI calculation: {rsi:.1f}")

    print()


if __name__ == "__main__":
    demo_stock_analysis()
    demo_technical_indicators_without_pandas()
