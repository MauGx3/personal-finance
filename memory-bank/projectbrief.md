# Project Brief

## Project Name

Personal Finance Management System

## Core Purpose

Build a comprehensive Django web application that enables users to track, manage, and analyze their financial assets, portfolios, and investment positions with precision and ease.

## Primary Goals

### 1. Asset Management

- Catalog financial assets globally (stocks, bonds, ETFs, crypto, etc.)
- Support international markets and currencies
- Maintain accurate asset identification (ticker, ISIN, CUSIP, SEDOL)
- Classify assets by type, sector, industry, and geography

### 2. Portfolio Tracking

- Allow users to create multiple portfolios
- Track individual asset holdings with quantity and cost basis
- Calculate portfolio values and performance metrics
- Support default portfolio designation

### 3. Financial Precision

- Use Decimal arithmetic for all financial calculations
- Avoid floating-point precision errors
- Maintain accurate cost basis and transaction history
- Support multiple currencies

### 4. User Experience

- Provide intuitive Django admin interface for data management
- Expose REST API for programmatic access and future integrations
- Enable quick asset lookups and portfolio views
- Support real-time data updates (future)

### 5. Data Integration

- Integrate with financial data providers for live pricing
- Support CSV/Excel import for bulk operations
- Enable export for reporting and tax purposes
- Connect to real-time market data feeds

## Success Criteria

1. **Data Accuracy**: All financial calculations must use Decimal precision
2. **Global Coverage**: Support 70+ countries and major international markets
3. **User Security**: Proper authentication and data isolation per user
4. **API First**: Well-documented REST API with OpenAPI/Swagger
5. **Testability**: Comprehensive unit tests with >80% coverage
6. **Performance**: Efficient database queries with proper indexing
7. **Extensibility**: Modular design allowing easy feature additions

## Key Constraints

- **Python Version**: Python 3.9+ for compatibility
- **Database**: PostgreSQL for reliability and advanced features
- **Framework**: Django 4.2+ for LTS support
- **Architecture**: Monolithic Django app with modular apps structure
- **Financial Accuracy**: Mandatory use of Decimal fields for all money/quantity values
- **Authentication**: Django Allauth for user management

## Non-Goals (Out of Scope)

- Real-time trading execution
- Financial advice or recommendations
- Cryptocurrency wallet management
- Tax filing automation (reporting only)
- Mobile native apps (web-first approach)
- Social features or sharing

## Target Users

1. **Individual Investors**: Track personal investment portfolios
2. **Financial Enthusiasts**: Monitor multiple asset classes globally
3. **Developers**: API access for custom integrations
4. **Administrators**: Manage asset catalog and user data

## Technical Approach

- **Backend**: Django with Django REST Framework
- **Database**: PostgreSQL with proper constraints and indexes
- **Package Manager**: uv for fast, reliable dependency management
- **API Documentation**: Automatic OpenAPI/Swagger generation
- **Testing**: Django TestCase with comprehensive coverage
- **Admin**: Django admin with custom configuration
- **Deployment**: Docker containers with docker-compose

## Timeline Phases

### Phase 1: Foundation ✅

- Django project setup
- PostgreSQL database configuration
- User authentication with Django Allauth
- Basic project structure

### Phase 2: Asset Management ✅

- Asset model with global coverage
- Portfolio and Holding models
- Database migrations and constraints
- Admin interface configuration
- REST API serializers
- Unit tests (7 passing)

### Phase 3: Data Integration (Next)

- Financial data API integration
- Live pricing updates
- Historical data storage
- Real-time websocket support

### Phase 4: Analytics & Reporting

- Portfolio performance calculations
- Tax reporting features
- Export functionality
- Advanced analytics

## Measuring Success

- **Functionality**: All core features working and tested
- **Performance**: API response times < 200ms
- **Reliability**: 99.9% uptime for production
- **Data Quality**: Zero precision errors in financial calculations
- **User Adoption**: Track active users and portfolio creation
- **API Usage**: Monitor API endpoint utilization

## Current Status

**Phase 2 Complete** - Asset management system fully implemented with Asset, Portfolio, and Holding models. Database contains example AAPL asset. Ready for Phase 3 data integration.
