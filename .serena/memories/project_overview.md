# Personal Finance Platform - Project Overview

## Purpose
A comprehensive personal finance management tool built with Django that provides:
- Portfolio management with real-time stock prices
- Performance tracking and analysis
- Historical data storage and retrieval 
- Backtesting engine for investment strategies
- Tax reporting and optimization
- Real-time WebSocket connections
- Visualization and analytics

## Tech Stack
- **Backend**: Django 5.1+ with Python 3.13
- **Database**: PostgreSQL (with SQLite fallback)
- **API**: Django REST Framework with drf-spectacular
- **Real-time**: WebSocket support via Django Channels
- **Financial Data**: Yahoo Finance, Alpha Vantage APIs
- **Analytics**: Pandas, NumPy, Matplotlib, Plotly
- **Testing**: Pytest with Django integration
- **Task Queue**: Celery with Redis
- **Authentication**: Django Allauth with MFA support

## Project Structure
```
personal-finance/
├── personal_finance/          # Main Django app package
│   ├── assets/               # Asset models and management
│   ├── portfolios/           # Portfolio management  
│   ├── analytics/            # Performance analytics
│   ├── backtesting/          # Strategy backtesting
│   ├── tax/                  # Tax calculations
│   ├── visualization/        # Charts and dashboards
│   ├── realtime/            # WebSocket real-time features
│   ├── data_sources/        # External data integration
│   └── users/               # Custom user model
├── config/                   # Django settings and configuration
├── tests/                    # Test suite
├── requirements/             # Dependencies
└── manage.py                # Django management
```

## Key Django Apps
- **assets**: Asset, Portfolio, Holding models (✅ migrated)
- **portfolios**: Position, Transaction models (❌ not migrated - 347 lines)
- **backtesting**: Strategy, Backtest models (❌ not migrated - 715 lines)  
- **tax**: TaxLot, TaxYear models (❌ not migrated - 467 lines)
- **analytics, data_sources, visualization, realtime**: Additional apps (❌ not migrated)

## Current Testing State
The project has extensive test documentation but limited working tests due to migration issues:
- **Working**: test_minimal_core.py (Django basics only)
- **Disabled**: Comprehensive test suite files (*.disabled) due to missing migrations
- **Coverage Goal**: 95%+ for models, 90%+ for APIs, 100% for financial calculations