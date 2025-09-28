System Architecture Overview
============================

The Personal Finance Platform follows a modular, service-oriented architecture built on Django with Celery for asynchronous processing.

.. contents:: Table of Contents
   :local:
   :depth: 2

High-Level Architecture
-----------------------

.. code-block:: text

   ┌─────────────────────────────────────────────────────────────────┐
   │                        Presentation Layer                       │
   ├─────────────────────────────────────────────────────────────────┤
   │ Django Templates │ REST API │ WebSocket │ Static Assets         │
   │                  │ (DRF)    │ (Channels)│                       │
   └─────────────────────────────────────────────────────────────────┘
                                       │
   ┌─────────────────────────────────────────────────────────────────┐
   │                       Application Layer                         │
   ├─────────────────────────────────────────────────────────────────┤
   │ Analytics │ Backtesting │ Tax │ Realtime │ Visualization       │
   │ Services  │ Engine      │ Calc│ Feeds    │ Dashboards          │
   └─────────────────────────────────────────────────────────────────┘
                                       │
   ┌─────────────────────────────────────────────────────────────────┐
   │                         Domain Layer                            │
   ├─────────────────────────────────────────────────────────────────┤
   │ Portfolio │ Assets │ Users │ Transactions │ Data Sources       │
   │ Models    │ Models │ Models│ Models       │ Adapters            │
   └─────────────────────────────────────────────────────────────────┘
                                       │
   ┌─────────────────────────────────────────────────────────────────┐
   │                      Infrastructure Layer                       │
   ├─────────────────────────────────────────────────────────────────┤
   │ PostgreSQL │ Redis │ Celery │ File Storage │ External APIs     │
   │ Database   │ Cache │ Worker │              │ (Yahoo Finance)    │
   └─────────────────────────────────────────────────────────────────┘

Core Components
---------------

Django Application Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The application is organized into focused Django apps:

.. code-block:: text

   personal_finance/
   ├── analytics/          # Portfolio analytics and metrics
   ├── assets/             # Asset management and price data
   ├── backtesting/        # Strategy simulation engine
   ├── contrib/            # Third-party integrations
   ├── data_profiler/      # Data validation and profiling
   ├── data_sources/       # Market data adapters
   ├── portfolios/         # Portfolio and position management
   ├── realtime/           # WebSocket streaming services
   ├── tax/                # Tax calculation and reporting
   ├── users/              # User management and authentication
   └── visualization/      # Charting and dashboard services

Configuration and Routing
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   config/
   ├── settings/           # Environment-specific settings
   │   ├── base.py         # Common settings
   │   ├── local.py        # Development settings
   │   ├── production.py   # Production settings
   │   └── test.py         # Testing settings
   ├── urls.py             # Main URL routing
   ├── api_router.py       # API endpoint routing
   ├── asgi.py             # ASGI application (WebSockets)
   ├── wsgi.py             # WSGI application (traditional HTTP)
   └── celery_app.py       # Celery configuration

Data Flow Architecture
----------------------

Request Processing Flow
~~~~~~~~~~~~~~~~~~~~~~~

1. **HTTP Requests**: Routed through Django's URL dispatcher
2. **API Requests**: Handled by Django REST Framework serializers/viewsets
3. **WebSocket Connections**: Managed by Django Channels consumers
4. **Background Tasks**: Queued via Celery for asynchronous processing

Data Processing Pipeline
~~~~~~~~~~~~~~~~~~~~~~~~

.. mermaid::

   graph TD
       A[External Data Sources] --> B[Data Ingestion]
       B --> C[Data Validation]
       C --> D[Data Storage]
       D --> E[Analytics Processing]
       E --> F[Real-time Updates]
       F --> G[Client Applications]

Service Layer Pattern
---------------------

Each domain module follows a consistent service layer pattern:

.. code-block:: python

   # Example: Analytics Service Structure
   analytics/
   ├── __init__.py
   ├── models.py           # Data models
   ├── services.py         # Business logic services
   ├── serializers.py      # API serialization
   ├── views.py            # HTTP request handlers
   ├── consumers.py        # WebSocket consumers
   ├── tasks.py            # Celery background tasks
   ├── admin.py            # Django admin integration
   └── tests/              # Test suite

Service Interfaces
~~~~~~~~~~~~~~~~~~

All services implement consistent interfaces:

.. code-block:: python

   class BaseService:
       """Base service class with common patterns."""

       def __init__(self, user=None):
           self.user = user

       def validate_permissions(self, obj):
           """Check user permissions for object access."""
           pass

       def get_queryset(self):
           """Return filtered queryset for user."""
           pass

Background Processing
---------------------

Celery Task Architecture
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   Background Tasks:
   ├── Data Ingestion Tasks
   │   ├── fetch_market_data.py
   │   ├── update_asset_prices.py
   │   └── import_transactions.py
   ├── Analytics Tasks
   │   ├── calculate_portfolio_metrics.py
   │   ├── generate_performance_reports.py
   │   └── update_risk_metrics.py
   ├── Tax Processing Tasks
   │   ├── calculate_capital_gains.py
   │   ├── identify_tax_lots.py
   │   └── generate_tax_reports.py
   └── Maintenance Tasks
       ├── cleanup_old_data.py
       ├── backup_database.py
       └── system_health_checks.py

Task Queue Strategy
~~~~~~~~~~~~~~~~~~~

* **High Priority**: Real-time price updates, user-initiated calculations
* **Normal Priority**: Scheduled analytics, report generation
* **Low Priority**: Data cleanup, system maintenance

Security Architecture
---------------------

Authentication & Authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Session-based Authentication**: For web interface
* **Token Authentication**: For API access
* **Permission Framework**: Django's built-in permissions with custom extensions

Data Protection Layers
~~~~~~~~~~~~~~~~~~~~~~

1. **Input Validation**: All user inputs validated at API boundary
2. **SQL Injection Protection**: Django ORM with parameterized queries
3. **CSRF Protection**: Django's CSRF middleware
4. **XSS Protection**: Context-aware output encoding
5. **Sensitive Data Handling**: Encrypted storage for API keys

Scalability Considerations
--------------------------

Horizontal Scaling Points
~~~~~~~~~~~~~~~~~~~~~~~~~

* **Web Servers**: Multiple Django instances behind load balancer
* **Background Workers**: Multiple Celery worker processes
* **Database**: Read replicas for analytics queries
* **Cache Layer**: Redis cluster for session and data caching

Performance Optimizations
~~~~~~~~~~~~~~~~~~~~~~~~~

* **Database Indexing**: Strategic indexes on high-frequency queries
* **Query Optimization**: Use of select_related and prefetch_related
* **Caching Strategy**: Multi-level caching (Redis, Django cache framework)
* **Static Assets**: CDN delivery for CSS/JS/images

Monitoring & Observability
--------------------------

Health Check Endpoints
~~~~~~~~~~~~~~~~~~~~~~

* ``/health/`` - Basic application health
* ``/health/database/`` - Database connectivity
* ``/health/cache/`` - Redis connectivity
* ``/health/celery/`` - Background worker status

Logging Architecture
~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   Logging Hierarchy:
   ├── Application Logs
   │   ├── personal_finance.analytics
   │   ├── personal_finance.backtesting
   │   └── personal_finance.realtime
   ├── Infrastructure Logs
   │   ├── django.db.backends
   │   ├── celery.worker
   │   └── channels.consumer
   └── Security Logs
       ├── django.security
       └── personal_finance.auth

Deployment Architecture
-----------------------

Production Topology
~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   Production Environment:
   ├── Load Balancer (Nginx)
   ├── Application Servers (Django + Gunicorn)
   ├── Background Workers (Celery)
   ├── Message Broker (Redis)
   ├── Database (PostgreSQL)
   ├── File Storage (Local/S3)
   └── Monitoring (Logs + Metrics)

Container Strategy
~~~~~~~~~~~~~~~~~~

* **Application Container**: Django app with Gunicorn
* **Worker Container**: Celery workers
* **Database Container**: PostgreSQL with persistent volumes
* **Cache Container**: Redis for sessions and caching

See Also
--------

* :doc:`database` - Database schema and models
* :doc:`services` - Service layer implementation details
* :doc:`data_flow` - Detailed data processing flows
* :doc:`../deployment/docker` - Container deployment guide
