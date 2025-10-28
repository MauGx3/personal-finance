# Active Context

Last updated: 2025-10-28

## Current Work Focus

**Asset Management System - COMPLETED ✅**

We have successfully implemented a comprehensive asset management system for tracking financial portfolios. The system is now ready for use and testing.

## Recent Changes

### Asset Catalog (Completed)

- ✅ Created `Asset` model with comprehensive fields:
  - Ticker, name, asset_type (10+ types: stock, bond, ETF, crypto, etc.)
  - Country (70+ choices covering global markets)
  - Market identification (NASDAQ, NYSE, LSE, etc.)
  - Financial identifiers: ISIN, CUSIP, SEDOL
  - Sector and industry classification
  - Currency support (USD, EUR, GBP, etc.)
  - Active status and metadata JSON field
- ✅ Database migration `0001_initial.py` applied successfully

### Portfolio Management (Completed)

- ✅ Created `Portfolio` model:
  - User relationship (one-to-many)
  - Portfolio name and description
  - Default portfolio designation (only one per user)
  - Active status tracking
  - Computed properties: total_value, holdings_count
- ✅ Created `Holding` model:
  - Links user, asset, and portfolio
  - Tracks quantity and average_price (Decimal fields)
  - Supports multiple currencies
  - Transaction timestamps (acquired_at, last_transaction_at)
  - Computed cost basis: quantity × average_price
  - Placeholder methods for future pricing: current_value, unrealized_gain_loss
  - Unique constraint: prevents duplicate holdings per user/asset/portfolio
  - Check constraint: ensures quantity is non-negative
- ✅ Database migration `0002_portfolio_holding_and_more.py` applied successfully

### Admin Interface (Completed)

- ✅ `AssetAdmin`: Full CRUD with filtering (type, country, market, sector) and search (ticker, name, ISIN)
- ✅ `PortfolioAdmin`: List view with holdings_count and total_value, user filtering
- ✅ `HoldingAdmin`: Comprehensive view with asset/portfolio details, financial calculations display, raw_id_fields for performance

### REST API (Completed)

- ✅ Asset serializers: AssetSerializer, AssetListSerializer, AssetCreateSerializer
- ✅ Portfolio serializers: PortfolioSerializer, PortfolioListSerializer
- ✅ Holding serializers: HoldingSerializer, HoldingListSerializer, HoldingCreateSerializer
- ✅ Validation: regex patterns for financial identifiers, positive quantity/price checks
- ✅ Display fields: get_*_display() methods for choice fields, related object details

### Testing (Completed)

- ✅ 7 unit tests passing in `apps/assets/tests/test_models.py`
- ✅ Tests cover: asset creation, portfolio defaults, holding calculations, validation, relationships

### Example Data (Completed)

- ✅ AAPL (Apple Inc.) asset added to database:
  - Ticker: AAPL
  - Type: Stock
  - Market: NASDAQ
  - Country: US
  - ISIN: US0378331005
  - Sector: Technology
  - Industry: Consumer Electronics

### Landing Page Integration (Completed)

- ✅ Added "Assets Database" link to development landing page
- ✅ Quick access to admin interface from homepage

## Next Steps

### Immediate (Phase 3)

1. **Financial Data Integration**
   - Integrate yfinance or similar API for market data
   - Implement current_value calculation using live prices
   - Add price_history model for historical data storage
   - Schedule periodic price updates via Celery tasks

2. **Real-time Updates**
   - Implement websocket support for live price feeds
   - Add price change notifications
   - Build streaming price updates for portfolio view

3. **API Endpoints**
   - Create viewsets for Asset, Portfolio, Holding models
   - Wire up URL routing in `apps/assets/urls.py`
   - Add authentication requirements
   - Test API with Swagger UI

### Near-term (Phase 4)

4. **Performance Calculations**
   - Implement unrealized_gain_loss based on current prices
   - Calculate portfolio-level metrics (total value, total gain/loss, % return)
   - Add time-weighted and money-weighted returns
   - Historical performance tracking

5. **Transaction History**
   - Create Transaction model (buy, sell, dividend, split)
   - Link transactions to holdings
   - Automatic average_price calculation from transactions
   - Transaction import from CSV

6. **Reporting & Export**
   - Portfolio summary reports
   - Holdings by asset type/country/sector
   - CSV/Excel export functionality
   - Tax reporting (capital gains, dividends)

### Long-term (Phase 5)

7. **Advanced Features**
   - Multi-currency support with exchange rates
   - Dividend tracking and reinvestment
   - Asset allocation analysis
   - Rebalancing recommendations
   - Backtesting portfolio strategies

## Active Decisions

### Technical Choices

- **Decimal Fields**: Using Django DecimalField for all financial values to ensure precision
- **Placeholder Methods**: current_value and unrealized_gain_loss return Decimal("0.00") until pricing API integrated
- **Unique Constraints**: Preventing duplicate holdings at database level
- **Soft Deletion**: Using is_active flags instead of hard deletes
- **JSON Metadata**: Flexible storage for asset-specific or holding-specific extra data

### API Design

- **List Serializers**: Lightweight versions for performance in list views
- **Create Serializers**: Separate serializers with input validation
- **User Context**: Holdings/Portfolios automatically associated with authenticated user
- **Display Fields**: Including human-readable versions of choice fields

### Testing Strategy

- **Unit Tests**: Focus on model logic, calculations, and constraints
- **No Network Tests**: Mock external APIs to avoid network dependencies
- **Decimal Assertions**: Verify financial calculations with exact precision

## Current Blockers

**None** - Asset management system is complete and functional.

## Questions/Uncertainties

1. **Pricing API Selection**: Which financial data provider to use?
   - Options: yfinance (free, limited), Alpha Vantage (API key required), Polygon.io (paid)
   - Decision: Start with yfinance for development, consider paid APIs for production

2. **Real-time vs Polling**: How to deliver price updates?
   - Websockets for real-time (complex, resource-intensive)
   - Periodic polling with Celery (simpler, delayed)
   - Decision: Implement polling first, add websockets later if needed

3. **Multi-currency**: How to handle currency conversion?
   - Store all values in original currency
   - Convert for display using exchange rates
   - Need exchange rate data source and update mechanism

4. **Historical Data**: How much price history to store?
   - Daily close prices for backtesting
   - Intraday for day-trading users
   - Storage costs vs query performance
   - Decision: Start with daily, add intraday on demand

## Notes for Next Session

- The asset management foundation is solid and ready for pricing integration
- All models use Decimal fields ensuring financial accuracy
- Database schema supports future features (transactions, dividends, splits)
- Admin interface provides quick way to test and manage data
- API structure is in place, just needs viewset wiring
- Example AAPL asset demonstrates complete data flow

## Development Environment

- **Package Manager**: uv (fast, Rust-based)
- **Database**: PostgreSQL locally
- **Server**: `uv run python manage.py runserver`
- **Tests**: `uv run python manage.py test apps.assets.tests`
- **Migrations**: `uv run python manage.py makemigrations` / `migrate`
- **Shell**: `uv run python manage.py shell -c '<code>'`
