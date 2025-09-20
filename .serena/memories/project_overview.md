# Personal Finance Platform - Project Overview

## Purpose
A comprehensive personal finance management platform built with Django that provides:
- Portfolio management with real-time stock prices
- Performance tracking and analytics
- Historical data storage and retrieval
- Tax compliance and reporting
- Backtesting strategies
- Real-time data feeds

## Tech Stack
- **Backend**: Django 5.1.x with Python 3.10+
- **Database**: PostgreSQL (with SQLite fallback)
- **API**: Django REST Framework
- **Frontend**: Django templates + real-time WebSocket features
- **External APIs**: Yahoo Finance, Alpha Vantage
- **Caching**: Redis
- **Task Queue**: Celery
- **Testing**: pytest with pytest-django

## Architecture
The project follows Django app structure:
- `assets/` - Core asset and portfolio models (MIGRATED)
- `users/` - User management (MIGRATED) 
- `tax/` - Tax calculations and compliance (MIGRATED)
- `portfolios/` - Portfolio management (NO MIGRATIONS - needs work)
- `backtesting/` - Strategy backtesting (NO MIGRATIONS - needs work)
- `analytics/` - Performance analytics (NO MIGRATIONS)
- `data_sources/` - External data integration (NO MIGRATIONS)
- `visualization/` - Charts and graphs (NO MIGRATIONS)
- `realtime/` - WebSocket features (NO MIGRATIONS)

## Current State
The project has been streamlined due to CI/CD failures. Only apps with proper migrations are currently testable.