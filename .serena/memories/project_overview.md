# Personal Finance Management Tool - Project Overview

## Purpose
A comprehensive personal finance management tool built with Django and Python that integrates with PostgreSQL for data persistence. It provides portfolio management, real-time stock prices, performance tracking, and analysis capabilities.

## Tech Stack
- **Backend**: Django 5.1+ with Django REST Framework
- **Web Server**: Uvicorn with ASGI, Gunicorn for production
- **Database**: PostgreSQL (primary), SQLite (fallback for development)
- **Data Processing**: Pandas, NumPy, Polars recommended for finance
- **Financial APIs**: Yahoo Finance (yfinance), Alpha Vantage, stockdex
- **Caching**: Redis, Django cache framework
- **Task Queue**: Celery with Django-Celery-Beat
- **Monitoring**: Built-in health checks
- **Frontend**: Django templates with Crispy Forms, Bootstrap 5
- **Visualization**: Plotly, Dash for interactive charts
- **Analytics**: QuantStats, scikit-learn, statsmodels

## Key Features
- Portfolio management with real-time stock prices
- Performance tracking and analysis with financial metrics
- Historical data storage and retrieval
- Tax compliance calculations
- Data validation and profiling
- Real-time data updates
- REST API endpoints
- Multi-user support with authentication