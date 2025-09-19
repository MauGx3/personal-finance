# Stock Analysis Implementation

This document describes the comprehensive stock analysis features implemented in the personal finance application.

## Overview

The stock analysis module provides a complete framework for analyzing stocks including:

- **Financial Analysis**: Income statement, balance sheet, cash flow analysis
- **Technical Analysis**: 15+ technical indicators and trading signals
- **Market Data**: Real-time quotes, sentiment analysis, sector comparisons
- **Valuation Analysis**: Multiple valuation models and fair value estimates
- **Risk Analysis**: Beta, volatility, VaR calculations
- **Investment Recommendations**: Automated scoring and recommendations

## Key Components

### 1. Stock Analysis Service (`stock_analysis.py`)

Main service class that orchestrates comprehensive stock analysis.

#### Data Structures

```python
@dataclass
class FinancialRatios:
    """Complete set of financial ratios."""
    # Profitability Ratios
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    roe: Optional[float] = None  # Return on Equity
    roa: Optional[float] = None  # Return on Assets
    roic: Optional[float] = None  # Return on Invested Capital
    
    # Liquidity Ratios
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    cash_ratio: Optional[float] = None
    
    # Leverage Ratios
    debt_to_equity: Optional[float] = None
    debt_to_assets: Optional[float] = None
    interest_coverage: Optional[float] = None
    
    # Efficiency Ratios
    asset_turnover: Optional[float] = None
    inventory_turnover: Optional[float] = None
    receivables_turnover: Optional[float] = None
    
    # Valuation Ratios
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    ps_ratio: Optional[float] = None
    ev_ebitda: Optional[float] = None
    peg_ratio: Optional[float] = None

@dataclass
class CompanyFinancials:
    """Company financial data structure."""
    symbol: str
    company_name: Optional[str] = None
    
    # Income Statement
    revenue: Optional[float] = None
    gross_profit: Optional[float] = None
    operating_income: Optional[float] = None
    net_income: Optional[float] = None
    eps: Optional[float] = None
    
    # Balance Sheet
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    shareholders_equity: Optional[float] = None
    cash_and_equivalents: Optional[float] = None
    total_debt: Optional[float] = None
    
    # Cash Flow Statement
    operating_cash_flow: Optional[float] = None
    free_cash_flow: Optional[float] = None
    capex: Optional[float] = None
    
    # Market Data
    market_cap: Optional[float] = None
    enterprise_value: Optional[float] = None
    shares_outstanding: Optional[float] = None
    current_price: Optional[float] = None
    
    # Ratios
    financial_ratios: Optional[FinancialRatios] = None
```

#### Core Methods

```python
class StockAnalysisService:
    def analyze_stock(self, symbol: str) -> StockAnalysisResult:
        """Perform comprehensive stock analysis."""
        
    def _get_company_financials(self, symbol: str) -> Optional[CompanyFinancials]:
        """Get company financial data from data sources."""
        
    def _calculate_financial_ratios(self, financials: CompanyFinancials) -> FinancialRatios:
        """Calculate 15+ financial ratios."""
        
    def _perform_technical_analysis(self, symbol: str) -> Dict[str, Any]:
        """Perform technical analysis using indicators."""
        
    def _perform_valuation_analysis(self, symbol: str, financials: Optional[CompanyFinancials]) -> Dict[str, Any]:
        """Perform valuation analysis."""
        
    def _calculate_overall_score(self, analysis_result: StockAnalysisResult) -> Optional[float]:
        """Calculate overall investment score (0-100)."""
```

### 2. Enhanced Technical Indicators (`services.py`)

Extended the existing technical indicators with 10+ new indicators:

#### New Indicators Added

1. **Stochastic Oscillator** - Momentum indicator comparing closing price to price range
2. **Williams %R** - Momentum indicator similar to stochastic
3. **Commodity Channel Index (CCI)** - Trend-following indicator
4. **Average True Range (ATR)** - Volatility indicator
5. **Parabolic SAR** - Trend-following indicator providing stop-loss levels
6. **Volume Weighted Average Price (VWAP)** - Trading benchmark
7. **On Balance Volume (OBV)** - Volume-momentum indicator
8. **Money Flow Index (MFI)** - Volume-weighted RSI
9. **Ichimoku Cloud** - Complete trend analysis system

#### Usage Examples

```python
from personal_finance.analytics.services import TechnicalIndicators

# Stochastic Oscillator
stoch = TechnicalIndicators.stochastic_oscillator(high, low, close)
print(f"%K: {stoch['%K'].iloc[-1]:.1f}")
print(f"%D: {stoch['%D'].iloc[-1]:.1f}")

# Williams %R
williams = TechnicalIndicators.williams_r(high, low, close)
print(f"Williams %R: {williams.iloc[-1]:.1f}")

# Commodity Channel Index
cci = TechnicalIndicators.commodity_channel_index(high, low, close)
print(f"CCI: {cci.iloc[-1]:.1f}")

# Average True Range
atr = TechnicalIndicators.average_true_range(high, low, close)
print(f"ATR: {atr.iloc[-1]:.2f}")

# Volume Weighted Average Price
vwap = TechnicalIndicators.volume_weighted_average_price(high, low, close, volume)
print(f"VWAP: ${vwap.iloc[-1]:.2f}")

# Money Flow Index
mfi = TechnicalIndicators.money_flow_index(high, low, close, volume)
print(f"MFI: {mfi.iloc[-1]:.1f}")

# Ichimoku Cloud
ichimoku = TechnicalIndicators.ichimoku_cloud(high, low, close)
print(f"Tenkan-sen: ${ichimoku['tenkan_sen'].iloc[-1]:.2f}")
print(f"Kijun-sen: ${ichimoku['kijun_sen'].iloc[-1]:.2f}")
```

### 3. REST API Endpoints (`api/stock_views.py`)

Comprehensive API for stock analysis with caching and error handling.

#### Available Endpoints

1. **`/api/stock/{symbol}/analysis/`** - Complete stock analysis
2. **`/api/stock/{symbol}/financials/`** - Detailed financial statements
3. **`/api/stock/{symbol}/technical/`** - Technical analysis indicators
4. **`/api/stock/{symbol}/quote/`** - Real-time quote data
5. **`/api/stock/{symbol}/sentiment/`** - Market sentiment analysis
6. **`/api/stock/{symbol}/sector-comparison/`** - Sector comparison
7. **`/api/stocks/compare/`** - Multi-stock comparison

#### API Response Examples

```json
// GET /api/stock/AAPL/analysis/
{
  "symbol": "AAPL",
  "analysis_date": "2024-01-15T10:30:00Z",
  "financials": {
    "symbol": "AAPL",
    "company_name": "Apple Inc.",
    "income_statement": {
      "revenue": 394328000000,
      "net_income": 99803000000,
      "eps": 6.13
    },
    "financial_ratios": {
      "profitability": {
        "gross_margin": 0.434,
        "net_margin": 0.253,
        "roe": 0.175
      },
      "valuation": {
        "pe_ratio": 28.7,
        "pb_ratio": 5.8
      }
    }
  },
  "technical_indicators": {
    "moving_averages": {
      "sma_20": 150.25,
      "sma_50": 148.75
    },
    "momentum": {
      "rsi": 65.3,
      "macd": 2.45
    }
  },
  "overall_assessment": {
    "overall_score": 75.2,
    "recommendation": "Buy"
  }
}
```

```json
// POST /api/stocks/compare/
{
  "symbols": ["AAPL", "GOOGL", "MSFT"],
  "comparison": {
    "AAPL": {
      "symbol": "AAPL",
      "overall_score": 75.2,
      "recommendation": "Buy",
      "pe_ratio": 28.7,
      "market_cap": 2800000000000
    },
    "GOOGL": {
      "symbol": "GOOGL", 
      "overall_score": 72.1,
      "recommendation": "Buy",
      "pe_ratio": 23.4,
      "market_cap": 1600000000000
    }
  }
}
```

### 4. Market Data Integration

Enhanced data sources integration for comprehensive market data.

#### Data Source Enhancements

```python
class StockdexSource(DataSourceBase):
    def get_company_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company information including sector, industry, etc."""
        
    def get_financial_statements(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get income statement, balance sheet, cash flow data."""

class MarketDataService:
    def get_real_time_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time stock quote with bid/ask."""
        
    def get_market_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Get analyst ratings and price targets."""
        
    def compare_with_sector(self, symbol: str, sector: str) -> Dict[str, Any]:
        """Compare stock performance with sector average."""
```

### 5. Caching and Performance

Implemented intelligent caching for different data types:

- **Analysis Results**: 1 hour cache
- **Financial Data**: 6 hour cache  
- **Technical Data**: 15 minute cache
- **Market Sentiment**: 4 hour cache
- **Real-time Quotes**: No cache (always fresh)

## Usage Examples

### Basic Stock Analysis

```python
from personal_finance.analytics.stock_analysis import StockAnalysisService

service = StockAnalysisService()
result = service.analyze_stock("AAPL")

print(f"Overall Score: {result.overall_score}")
print(f"Recommendation: {result.recommendation}")
print(f"P/E Ratio: {result.financials.financial_ratios.pe_ratio}")
```

### Technical Analysis

```python
from personal_finance.analytics.services import TechnicalIndicators

# Calculate multiple indicators
indicators = service._perform_technical_analysis("AAPL")
print(f"RSI: {indicators['momentum']['rsi']}")
print(f"MACD: {indicators['momentum']['macd']}")
```

### API Usage

```bash
# Get complete analysis
curl -X GET "http://localhost:8000/api/stock/AAPL/analysis/"

# Compare multiple stocks
curl -X POST "http://localhost:8000/api/stocks/compare/" \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "GOOGL", "MSFT"]}'
```

## Testing

Comprehensive test suite covering:

- Financial ratio calculations
- Technical indicator accuracy
- API endpoint functionality
- Data source integration
- Caching behavior

```bash
# Run tests
python -m pytest tests/test_stock_analysis.py -v
```

## Integration Points

The stock analysis module integrates with:

1. **Data Sources**: Uses existing data source management for fetching market data
2. **Analytics**: Extends existing analytics framework 
3. **Caching**: Uses Django cache framework for performance
4. **API**: Follows existing API patterns and authentication
5. **Models**: Can integrate with Asset and Portfolio models

## Future Enhancements

Potential areas for expansion:

1. **Machine Learning**: Stock price prediction models
2. **Options Analysis**: Options pricing and Greeks calculation
3. **Portfolio Integration**: Portfolio-level analysis and optimization
4. **Alerts**: Real-time alerts for technical signals
5. **Backtesting**: Strategy backtesting capabilities
6. **News Sentiment**: News sentiment analysis integration

## Configuration

Add these settings to Django settings:

```python
# Cache configuration for stock analysis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Stock analysis settings
STOCK_ANALYSIS = {
    'DEFAULT_CACHE_TIMEOUT': 3600,  # 1 hour
    'FINANCIAL_CACHE_TIMEOUT': 21600,  # 6 hours
    'TECHNICAL_CACHE_TIMEOUT': 900,  # 15 minutes
    'MAX_COMPARISON_STOCKS': 10,
}
```

This implementation provides a solid foundation for comprehensive stock analysis while maintaining extensibility for future enhancements.