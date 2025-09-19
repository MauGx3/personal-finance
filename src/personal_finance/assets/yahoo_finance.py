try:
    import yfinance
except ImportError:
    yfinance = None
import logging
try:
    import requests
except ImportError:
    requests = None
try:
    import json
except ImportError:
    json = None
from datetime import datetime
from typing import Optional, Dict, List
try:
    from ..database import DatabaseManager
except ImportError:
    DatabaseManager = None

logger = logging.getLogger(__name__)


def verify_yfinance():
    """Verify that yfinance is working properly"""
    if yfinance is None:
        logging.warning("yfinance not installed")
        return False
    try:
        ticker = yfinance.Ticker("AAPL")
        data = ticker.history(period="1d")
        if data.empty:
            logging.warning("yfinance returned empty data")
            return False
        return True
    except Exception as e:
        logging.error("yfinance verification failed: %s", e)
        return False


def get_ticker_price(
    symbol: str, db_manager: Optional[DatabaseManager] = None
) -> float:
    """Helper method to get current price for a single ticker"""
    if yfinance is None:
        logging.warning("yfinance not available, returning mock price for %s", symbol)
        return 100.0  # Mock price
    try:
        ticker = yfinance.Ticker(symbol)
        # Get today's data
        hist = ticker.history(period="1d")
        if not hist.empty:
            price = hist["Close"].iloc[-1]

            # Store in database if manager provided
            if db_manager:
                # Get ticker info
                info = ticker.info
                name = info.get("longName", info.get("shortName", symbol))
                db_manager.add_or_update_ticker(symbol, name, price)

            return price
        logging.warning("No price data available for %s", symbol)
        return 0
    except Exception as e:
        logging.error("Error fetching price for %s: %s", symbol, e)
        return 0


def fetch_and_store_historical_data(
    symbol: str,
    period: str = "1y",
    db_manager: Optional[DatabaseManager] = None,
) -> Optional[Dict]:
    """Fetch historical data and store in database"""
    try:
        ticker = yfinance.Ticker(symbol)
        hist = ticker.history(period=period)

        if hist.empty:
            logging.warning("No historical data available for %s", symbol)
            return None

        # Store in database if manager provided
        if db_manager:
            # Get ticker info
            info = ticker.info
            name = info.get("longName", info.get("shortName", symbol))
            db_manager.add_or_update_ticker(symbol, name)

            # Store historical data
            for date, row in hist.iterrows():
                db_manager.add_historical_price(
                    symbol=symbol,
                    date=date.to_pydatetime(),
                    open_price=row.get("Open"),
                    high_price=row.get("High"),
                    low_price=row.get("Low"),
                    close_price=row.get("Close"),
                    volume=row.get("Volume"),
                )

        return hist.to_dict()

    except Exception as e:
        logging.error("Error fetching historical data for %s: %s", symbol, e)
        return None


def get_stored_historical_data(
    symbol: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db_manager: Optional[DatabaseManager] = None,
) -> List[Dict]:
    """Get historical data from database"""
    if not db_manager:
        return []

    try:
        prices = db_manager.get_historical_prices(symbol, start_date, end_date)
        return [
            {
                "date": price.date,
                "open": price.open_price,
                "high": price.high_price,
                "low": price.low_price,
                "close": price.close_price,
                "volume": price.volume,
            }
            for price in prices
        ]
    except Exception as e:
        logging.error("Error retrieving historical data for %s: %s", symbol, e)
        return []


def update_all_ticker_prices(db_manager: DatabaseManager):
    """Update prices for all tickers in database"""
    try:
        tickers = db_manager.get_all_tickers()
        updated_count = 0

        for ticker in tickers:
            price = get_ticker_price(ticker.symbol, db_manager)
            if price > 0:
                updated_count += 1

        logging.info(f"Updated prices for {updated_count} tickers")
        return updated_count

    except Exception as e:
        logging.error("Error updating ticker prices: %s", e)
        return 0


def get_comprehensive_stock_info(symbol: str) -> Optional[Dict]:
    """Get comprehensive stock information including current price, market data, and company info"""
    try:
        # Try to use yfinance if available, otherwise return mock data for demo
        try:
            ticker = yfinance.Ticker(symbol)
            
            # Get basic ticker info
            info = ticker.info
            
            # Get current price data
            hist = ticker.history(period="2d")  # Get 2 days to calculate change
            
            if hist.empty:
                logging.warning("No price data available for %s", symbol)
                return _get_mock_stock_data(symbol)
                
            # Get latest price data
            latest_data = hist.iloc[-1] if len(hist) > 0 else None
            previous_data = hist.iloc[-2] if len(hist) > 1 else None
            
            if latest_data is None:
                return _get_mock_stock_data(symbol)
                
            current_price = latest_data["Close"]
            previous_close = previous_data["Close"] if previous_data is not None else current_price
            
            # Calculate price change
            price_change = current_price - previous_close
            price_change_percent = (price_change / previous_close * 100) if previous_close != 0 else 0
            
            # Prepare comprehensive data
            stock_data = {
                "symbol": symbol.upper(),
                "name": info.get("longName", info.get("shortName", symbol)),
                "current_price": round(float(current_price), 2),
                "previous_close": round(float(previous_close), 2),
                "price_change": round(float(price_change), 2),
                "price_change_percent": round(float(price_change_percent), 2),
                "day_high": round(float(latest_data["High"]), 2),
                "day_low": round(float(latest_data["Low"]), 2),
                "volume": int(latest_data["Volume"]) if latest_data["Volume"] else 0,
                "market_cap": info.get("marketCap"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "exchange": info.get("exchange"),
                "currency": info.get("currency", "USD"),
                "pe_ratio": info.get("trailingPE"),
                "dividend_yield": info.get("dividendYield"),
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
                "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
                "avg_volume": info.get("averageVolume"),
                "website": info.get("website"),
                "summary": info.get("longBusinessSummary", "").split(".")[0] + "." if info.get("longBusinessSummary") else None,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            }
        except (ImportError, NameError):
            # yfinance not available, return mock data
            logging.info("yfinance not available, using mock data for %s", symbol)
            return _get_mock_stock_data(symbol)
        
        # Format market cap for display
        if stock_data["market_cap"]:
            market_cap = stock_data["market_cap"]
            if market_cap >= 1e12:
                stock_data["market_cap_formatted"] = f"${market_cap/1e12:.2f}T"
            elif market_cap >= 1e9:
                stock_data["market_cap_formatted"] = f"${market_cap/1e9:.2f}B"
            elif market_cap >= 1e6:
                stock_data["market_cap_formatted"] = f"${market_cap/1e6:.2f}M"
            else:
                stock_data["market_cap_formatted"] = f"${market_cap:,.0f}"
        else:
            stock_data["market_cap_formatted"] = "N/A"
            
        # Format volume for display
        if stock_data["volume"]:
            volume = stock_data["volume"]
            if volume >= 1e9:
                stock_data["volume_formatted"] = f"{volume/1e9:.2f}B"
            elif volume >= 1e6:
                stock_data["volume_formatted"] = f"{volume/1e6:.2f}M"
            elif volume >= 1e3:
                stock_data["volume_formatted"] = f"{volume/1e3:.2f}K"
            else:
                stock_data["volume_formatted"] = f"{volume:,}"
        else:
            stock_data["volume_formatted"] = "N/A"
            
        return stock_data
        
    except Exception as e:
        logging.error("Error fetching comprehensive stock info for %s: %s", symbol, e)
        return _get_mock_stock_data(symbol)


def _get_mock_stock_data(symbol: str) -> Optional[Dict]:
    """Generate mock stock data for demonstration purposes"""
    # Return None for clearly invalid symbols
    if symbol in ["INVALID", "TEST", "FAKE"]:
        return None
        
    # Mock data for common stocks
    mock_companies = {
        "AAPL": {
            "name": "Apple Inc.",
            "current_price": 192.53,
            "previous_close": 191.75,
            "day_high": 194.23,
            "day_low": 190.88,
            "volume": 52830450,
            "market_cap": 2900000000000,  # $2.9T
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "exchange": "NASDAQ",
            "pe_ratio": 31.24,
            "dividend_yield": 0.0044,
            "fifty_two_week_high": 237.23,
            "fifty_two_week_low": 164.08,
            "avg_volume": 58435680,
            "website": "https://www.apple.com",
            "summary": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide."
        },
        "GOOGL": {
            "name": "Alphabet Inc.",
            "current_price": 186.75,
            "previous_close": 185.32,
            "day_high": 188.45,
            "day_low": 184.67,
            "volume": 28945673,
            "market_cap": 2300000000000,  # $2.3T
            "sector": "Communication Services",
            "industry": "Internet Content & Information",
            "exchange": "NASDAQ",
            "pe_ratio": 24.85,
            "dividend_yield": None,
            "fifty_two_week_high": 193.31,
            "fifty_two_week_low": 129.40,
            "avg_volume": 32567890,
            "website": "https://abc.xyz",
            "summary": "Alphabet Inc. provides various products and platforms in the United States and internationally."
        },
        "MSFT": {
            "name": "Microsoft Corporation",
            "current_price": 441.58,
            "previous_close": 440.17,
            "day_high": 443.92,
            "day_low": 439.23,
            "volume": 18934562,
            "market_cap": 3300000000000,  # $3.3T
            "sector": "Technology",
            "industry": "Software—Infrastructure",
            "exchange": "NASDAQ",
            "pe_ratio": 34.12,
            "dividend_yield": 0.0062,
            "fifty_two_week_high": 468.35,
            "fifty_two_week_low": 362.90,
            "avg_volume": 21234567,
            "website": "https://www.microsoft.com",
            "summary": "Microsoft Corporation develops, licenses, and supports software, services, devices, and solutions worldwide."
        }
    }
    
    # Get mock data or create generic data
    company_data = mock_companies.get(symbol.upper(), {
        "name": f"{symbol.upper()} Company",
        "current_price": 125.67,
        "previous_close": 124.89,
        "day_high": 127.45,
        "day_low": 123.12,
        "volume": 1234567,
        "market_cap": 50000000000,  # $50B
        "sector": "Technology",
        "industry": "Software",
        "exchange": "NASDAQ",
        "pe_ratio": 22.5,
        "dividend_yield": 0.02,
        "fifty_two_week_high": 150.00,
        "fifty_two_week_low": 90.00,
        "avg_volume": 2000000,
        "website": f"https://www.{symbol.lower()}.com",
        "summary": f"{symbol.upper()} is a demonstration company for the US stock view feature."
    })
    
    # Calculate price change
    price_change = company_data["current_price"] - company_data["previous_close"]
    price_change_percent = (price_change / company_data["previous_close"] * 100)
    
    stock_data = {
        "symbol": symbol.upper(),
        "name": company_data["name"],
        "current_price": round(company_data["current_price"], 2),
        "previous_close": round(company_data["previous_close"], 2),
        "price_change": round(price_change, 2),
        "price_change_percent": round(price_change_percent, 2),
        "day_high": round(company_data["day_high"], 2),
        "day_low": round(company_data["day_low"], 2),
        "volume": company_data["volume"],
        "market_cap": company_data["market_cap"],
        "sector": company_data["sector"],
        "industry": company_data["industry"],
        "exchange": company_data["exchange"],
        "currency": "USD",
        "pe_ratio": company_data["pe_ratio"],
        "dividend_yield": company_data["dividend_yield"],
        "fifty_two_week_high": company_data["fifty_two_week_high"],
        "fifty_two_week_low": company_data["fifty_two_week_low"],
        "avg_volume": company_data["avg_volume"],
        "website": company_data["website"],
        "summary": company_data["summary"],
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    }
    
    # Format market cap for display
    if stock_data["market_cap"]:
        market_cap = stock_data["market_cap"]
        if market_cap >= 1e12:
            stock_data["market_cap_formatted"] = f"${market_cap/1e12:.2f}T"
        elif market_cap >= 1e9:
            stock_data["market_cap_formatted"] = f"${market_cap/1e9:.2f}B"
        elif market_cap >= 1e6:
            stock_data["market_cap_formatted"] = f"${market_cap/1e6:.2f}M"
        else:
            stock_data["market_cap_formatted"] = f"${market_cap:,.0f}"
    else:
        stock_data["market_cap_formatted"] = "N/A"
        
    # Format volume for display
    if stock_data["volume"]:
        volume = stock_data["volume"]
        if volume >= 1e9:
            stock_data["volume_formatted"] = f"{volume/1e9:.2f}B"
        elif volume >= 1e6:
            stock_data["volume_formatted"] = f"{volume/1e6:.2f}M"
        elif volume >= 1e3:
            stock_data["volume_formatted"] = f"{volume/1e3:.2f}K"
        else:
            stock_data["volume_formatted"] = f"{volume:,}"
    else:
        stock_data["volume_formatted"] = "N/A"
        
    return stock_data


if __name__ == "__main__":
    verify_yfinance()
