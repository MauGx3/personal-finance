# Product Context

## Why This Project Exists

Personal finance management is fragmented across multiple tools and platforms. Investors often struggle with:

- **Scattered Data**: Assets spread across different brokers and platforms
- **Manual Tracking**: Tedious spreadsheet maintenance prone to errors
- **Limited Visibility**: Difficulty seeing complete portfolio picture
- **Calculation Errors**: Floating-point precision issues in cost basis tracking
- **Global Complexity**: International assets and currencies require specialized tools
- **Data Privacy**: Concerns about sharing financial data with third parties

This project exists to provide a **self-hosted, accurate, and comprehensive** solution for tracking personal financial assets.

## Problems It Solves

### 1. Centralized Asset Catalog

**Problem**: Tracking assets across multiple brokers, countries, and asset types
**Solution**: Single database with 70+ countries, 10+ asset types, comprehensive identification (ISIN, CUSIP, SEDOL)

### 2. Portfolio Organization

**Problem**: Managing multiple investment strategies (retirement, growth, income, etc.)
**Solution**: User-defined portfolios with default designation and unlimited holdings per portfolio

### 3. Financial Precision

**Problem**: Spreadsheet rounding errors and floating-point arithmetic issues
**Solution**: Decimal-based calculations throughout, ensuring accurate cost basis and gains/losses

### 4. Data Ownership

**Problem**: Vendor lock-in and data privacy concerns with third-party services
**Solution**: Self-hosted Django application with PostgreSQL, complete data control

### 5. API Access

**Problem**: Limited automation and integration capabilities with existing tools
**Solution**: RESTful API with OpenAPI documentation for programmatic access

### 6. Global Asset Support

**Problem**: Most tools focus on US markets only
**Solution**: Support for international markets, currencies, and asset types

## How It Should Work

### User Journey

1. **Setup**
   - User creates account via Django Allauth authentication
   - System creates default portfolio automatically
   - User can create additional portfolios as needed

2. **Asset Management**
   - Admin interface or API to add assets to the catalog
   - Search assets by ticker, name, ISIN, etc.
   - Assets include comprehensive metadata (type, country, market, sector, industry)
   - Example: AAPL already in database with complete details

3. **Portfolio Building**
   - User selects assets from catalog
   - Creates holdings with quantity and average price
   - System calculates cost basis automatically
   - Holdings can be organized into different portfolios

4. **Tracking & Analysis**
   - View portfolio summaries with holdings count
   - Calculate total cost basis for each holding
   - Future: Real-time valuations via pricing API
   - Future: Performance analytics and gain/loss tracking

5. **Data Access**
   - Django admin for quick data management
   - REST API for programmatic access
   - Future: Export to CSV/Excel for reporting
   - Future: Real-time websocket updates

## User Experience Goals

### Simplicity

- Intuitive admin interface requires minimal training
- Logical data hierarchy: Asset → Portfolio → Holding
- Clear field labels and help text
- Sensible defaults (e.g., USD currency, active status)

### Accuracy

- Decimal precision for all financial values
- Validation of financial identifiers (ISIN format, etc.)
- Database constraints prevent invalid data
- Comprehensive test coverage ensures reliability

### Flexibility

- Support multiple portfolios per user
- Optional portfolio association for holdings
- Custom metadata via JSON fields
- Extensible choice fields for asset types and countries

### Performance

- Efficient database queries with select_related
- Proper indexing on frequently queried fields
- Lightweight list serializers for API responses
- Pagination support for large datasets

### Security

- Per-user data isolation via foreign keys
- Django authentication and permissions
- Admin interface access control
- API authentication (future: token-based)

## Success Metrics

### User Adoption

- Number of active users
- Portfolios created per user
- Holdings tracked per portfolio
- Asset catalog coverage

### Data Quality

- Zero financial calculation errors
- Valid asset identifiers (ISIN, CUSIP, SEDOL)
- Complete asset metadata
- Accurate cost basis tracking

### Technical Performance

- API response times < 200ms
- Database query optimization
- Test coverage > 80%
- Zero critical bugs in production

### Feature Completeness

- Phase 2 ✅: Asset management complete
- Phase 3 🔄: Data integration in progress
- Phase 4 ⏳: Analytics pending
- Phase 5 ⏳: Advanced features planned

## Current State

**Asset Management System**: Complete and tested

- ✅ Asset model with 70+ countries and 10+ asset types
- ✅ Portfolio model with default portfolio logic
- ✅ Holding model with cost basis calculations
- ✅ Django admin interface with filtering and search
- ✅ REST API with comprehensive serializers
- ✅ 7 unit tests passing
- ✅ Example data: AAPL (Apple Inc.) in database
- ✅ Database migration applied: 0002_portfolio_holding_and_more.py

**Next Steps**:

- 🔄 Integrate financial data APIs for live pricing
- 🔄 Implement current_value and unrealized_gain_loss calculations
- 🔄 Add real-time price updates via websockets
- 🔄 Build portfolio performance analytics
- 🔄 Create tax reporting features

## Design Philosophy

### Data-Driven

Every decision backed by clear use cases and user needs. Financial precision is non-negotiable.

### API-First

REST API provides flexibility for future frontends, mobile apps, or third-party integrations.

### Self-Hosted

Users maintain complete control over their financial data without vendor lock-in.

### Open Source

Transparent codebase allowing community contributions and security audits.

### Test-Driven

Comprehensive test coverage ensures reliability and facilitates refactoring.

### Django Patterns

Follow Django best practices: fat models, thin views, DRF for APIs, admin for quick CRUD.
