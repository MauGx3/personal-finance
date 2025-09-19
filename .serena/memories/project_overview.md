# Personal Finance Management Tool - Project Overview

## Purpose
A comprehensive personal finance management tool built with Django/Python that integrates financial data sources for portfolio management, backtesting, and analysis.

## Tech Stack
- **Backend**: Django 5.x web framework
- **Database**: PostgreSQL (with SQLite fallback)  
- **Data Processing**: pandas, numpy
- **Financial Data**: yfinance, alpha_vantage, stockdx
- **Analysis**: matplotlib, plotly, seaborn, quantstats
- **Task Queue**: Celery with Redis
- **Linting**: ruff, pylint
- **Testing**: pytest

## Architecture
- Django apps structure: backtesting, data_sources, analytics, portfolios, users, etc.
- Abstract base classes for strategies and data sources with concrete implementations
- Circuit breaker pattern for data source reliability
- Comprehensive backtesting engine for trading strategies

## Current Issue
The project has PYL-W0223 (Abstract method not overridden) violations where concrete classes inherit from abstract base classes but don't implement all required abstract methods.

## Key Files
- `personal_finance/backtesting/services.py` - Trading strategy implementations
- `personal_finance/data_sources/services.py` - Financial data source implementations
- `personal_finance/analytics/services.py` - Performance analytics and technical indicators