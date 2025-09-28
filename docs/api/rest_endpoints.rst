REST API Endpoints Reference
==============================

Complete reference for all REST API endpoints in the Personal Finance Platform.

.. contents:: Table of Contents
   :local:
   :depth: 2

API Overview
------------

Base URL
~~~~~~~~

All API endpoints are prefixed with:

.. code-block:: text

   http://localhost:8000/api/

Authentication
~~~~~~~~~~~~~~

The API supports multiple authentication methods:

* **Session Authentication**: For web interface integration
* **Token Authentication**: For programmatic access
* **API Key Authentication**: For service-to-service communication

.. code-block:: bash

   # Token authentication
   curl -H \"Authorization: Token your-token-here\" http://localhost:8000/api/

Response Format
~~~~~~~~~~~~~~~

All API responses follow this structure:

.. code-block:: json

   {
       \"results\": [...],     // For list endpoints
       \"count\": 100,         // Total count for paginated results
       \"next\": \"url\",        // Next page URL
       \"previous\": \"url\"     // Previous page URL
   }

Error responses:

.. code-block:: json

   {
       \"error\": \"error_code\",
       \"message\": \"Human readable error message\",
       \"details\": {...}      // Additional error context
   }

Pagination
~~~~~~~~~~

List endpoints support pagination:

* **Limit**: ``?limit=50`` (default: 20, max: 100)
* **Offset**: ``?offset=20``
* **Page**: ``?page=2`` (alternative to offset)

Portfolio Management
--------------------

Portfolio Endpoints
~~~~~~~~~~~~~~~~~~~~

.. http:get:: /api/portfolios/

   List user's portfolios.

   **Query Parameters:**

   * ``active_only`` (bool) - Filter to active portfolios only
   * ``ordering`` (str) - Sort order: ``name``, ``-created_at``, ``total_value``

   **Response:**

   .. code-block:: json

      {
          \"results\": [
              {
                  \"id\": 1,
                  \"name\": \"Growth Portfolio\",
                  \"description\": \"Long-term growth strategy\",
                  \"total_value\": \"125000.00\",
                  \"daily_change\": \"750.50\",
                  \"daily_change_percent\": \"0.60\",
                  \"position_count\": 15,
                  \"created_at\": \"2024-01-01T00:00:00Z\",
                  \"updated_at\": \"2024-01-15T10:30:00Z\"
              }
          ],
          \"count\": 1
      }

.. http:post:: /api/portfolios/

   Create a new portfolio.

   **Request:**

   .. code-block:: json

      {
          \"name\": \"Tech Portfolio\",
          \"description\": \"Technology sector focus\",
          \"benchmark_symbol\": \"QQQ\"
      }

.. http:get:: /api/portfolios/{id}/

   Get portfolio details.

.. http:put:: /api/portfolios/{id}/

   Update portfolio.

.. http:delete:: /api/portfolios/{id}/

   Delete portfolio.

Position Management
~~~~~~~~~~~~~~~~~~~

.. http:get:: /api/portfolios/{id}/positions/

   List positions in a portfolio.

   **Response:**

   .. code-block:: json

      {
          \"results\": [
              {
                  \"id\": 1,
                  \"asset\": {
                      \"id\": 1,
                      \"symbol\": \"AAPL\",
                      \"name\": \"Apple Inc.\",
                      \"current_price\": \"175.50\"
                  },
                  \"quantity\": \"100.00000000\",
                  \"average_cost\": \"150.25\",
                  \"current_value\": \"17550.00\",
                  \"unrealized_gain_loss\": \"2525.00\",
                  \"unrealized_gain_loss_percent\": \"16.79\",
                  \"last_updated\": \"2024-01-15T10:30:00Z\"
              }
          ]
      }

.. http:post:: /api/portfolios/{id}/positions/

   Add a position to portfolio.

   **Request:**

   .. code-block:: json

      {
          \"asset_symbol\": \"MSFT\",
          \"quantity\": \"50.00000000\",
          \"purchase_price\": \"380.25\",
          \"purchase_date\": \"2024-01-15\"
      }

Transaction Management
~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /api/transactions/

   List user's transactions.

   **Query Parameters:**

   * ``portfolio_id`` (int) - Filter by portfolio
   * ``asset_symbol`` (str) - Filter by asset symbol
   * ``transaction_type`` (str) - Filter by type: ``buy``, ``sell``, ``dividend``
   * ``date_from`` (date) - Start date filter
   * ``date_to`` (date) - End date filter

.. http:post:: /api/transactions/

   Record a new transaction.

   **Request:**

   .. code-block:: json

      {
          \"portfolio\": 1,
          \"asset_symbol\": \"GOOGL\",
          \"transaction_type\": \"buy\",
          \"quantity\": \"10.00000000\",
          \"price\": \"2850.75\",
          \"transaction_date\": \"2024-01-15\",
          \"fees\": \"9.99\"
      }

Asset Management
----------------

Asset Endpoints
~~~~~~~~~~~~~~~

.. http:get:: /api/assets/

   List available assets.

   **Query Parameters:**

   * ``symbol`` (str) - Filter by symbol
   * ``asset_type`` (str) - Filter by type: ``stock``, ``etf``, ``bond``, ``crypto``
   * ``sector`` (str) - Filter by sector
   * ``search`` (str) - Search by symbol or name

   **Response:**

   .. code-block:: json

      {
          \"results\": [
              {
                  \"id\": 1,
                  \"symbol\": \"AAPL\",
                  \"name\": \"Apple Inc.\",
                  \"asset_type\": \"stock\",
                  \"sector\": \"Technology\",
                  \"current_price\": \"175.50\",
                  \"price_change\": \"2.25\",
                  \"price_change_percent\": \"1.30\",
                  \"volume\": 50000000,
                  \"market_cap\": \"2750000000000\",
                  \"last_updated\": \"2024-01-15T16:00:00Z\"
              }
          ]
      }

.. http:get:: /api/assets/{id}/

   Get asset details.

.. http:get:: /api/assets/{id}/price-history/

   Get historical price data.

   **Query Parameters:**

   * ``days`` (int) - Number of days (default: 252)
   * ``interval`` (str) - Data interval: ``1d``, ``1h``, ``5m``

   **Response:**

   .. code-block:: json

      {
          \"symbol\": \"AAPL\",
          \"data\": [
              {
                  \"date\": \"2024-01-15\",
                  \"open\": \"174.25\",
                  \"high\": \"176.00\",
                  \"low\": \"173.50\",
                  \"close\": \"175.50\",
                  \"volume\": 45000000
              }
          ]
      }

Market Data
~~~~~~~~~~~

.. http:post:: /api/assets/bulk-prices/

   Get current prices for multiple assets.

   **Request:**

   .. code-block:: json

      {
          \"symbols\": [\"AAPL\", \"MSFT\", \"GOOGL\"]
      }

   **Response:**

   .. code-block:: json

      {
          \"prices\": {
              \"AAPL\": {
                  \"price\": \"175.50\",
                  \"change\": \"2.25\",
                  \"change_percent\": \"1.30\",
                  \"timestamp\": \"2024-01-15T16:00:00Z\"
              }
          }
      }

Backtesting API
---------------

Strategy Management
~~~~~~~~~~~~~~~~~~~

.. http:get:: /api/backtesting/strategies/

   List user's trading strategies.

.. http:post:: /api/backtesting/strategies/

   Create a new trading strategy.

   **Request:**

   .. code-block:: json

      {
          \"name\": \"Tech Momentum Strategy\",
          \"strategy_type\": \"moving_average\",
          \"description\": \"Moving average crossover for tech stocks\",
          \"parameters\": {
              \"short_window\": 20,
              \"long_window\": 50
          },
          \"initial_capital\": \"100000.00\",
          \"max_position_size\": \"0.25\",
          \"asset_symbols\": [\"AAPL\", \"MSFT\", \"GOOGL\", \"NVDA\"]
      }

.. http:get:: /api/backtesting/strategies/{id}/

   Get strategy details.

Backtest Execution
~~~~~~~~~~~~~~~~~~

.. http:get:: /api/backtesting/backtests/

   List user's backtests.

.. http:post:: /api/backtesting/backtests/

   Create a new backtest.

   **Request:**

   .. code-block:: json

      {
          \"strategy\": 1,
          \"name\": \"Q1 2024 Test\",
          \"start_date\": \"2024-01-01\",
          \"end_date\": \"2024-03-31\",
          \"benchmark_symbol\": \"SPY\",
          \"transaction_costs\": \"0.001\",
          \"slippage\": \"0.0005\"
      }

.. http:post:: /api/backtesting/backtests/{id}/run/

   Execute a backtest.

   **Response:**

   .. code-block:: json

      {
          \"status\": \"completed\",
          \"result\": {
              \"total_return\": \"15.42\",
              \"annualized_return\": \"18.23\",
              \"sharpe_ratio\": \"1.35\",
              \"max_drawdown\": \"-12.45\",
              \"total_trades\": 47,
              \"win_rate\": \"0.68\"
          },
          \"execution_time\": 2.34
      }

.. http:post:: /api/backtesting/quick-backtest/

   Create and run a backtest in one operation.

   **Request:**

   .. code-block:: json

      {
          \"strategy_type\": \"buy_hold\",
          \"asset_symbols\": [\"SPY\", \"QQQ\"],
          \"start_date\": \"2023-01-01\",
          \"end_date\": \"2024-01-01\",
          \"initial_capital\": 50000
      }

Analytics API
-------------

Portfolio Analytics
~~~~~~~~~~~~~~~~~~~

.. http:get:: /api/analytics/portfolio/{id}/metrics/

   Get portfolio performance metrics.

   **Query Parameters:**

   * ``period`` (str) - Analysis period: ``1m``, ``3m``, ``6m``, ``1y``, ``2y``
   * ``benchmark`` (str) - Benchmark symbol for comparison

   **Response:**

   .. code-block:: json

      {
          \"period\": \"1y\",
          \"total_return\": \"12.45\",
          \"annualized_return\": \"12.45\",
          \"volatility\": \"18.32\",
          \"sharpe_ratio\": \"0.68\",
          \"max_drawdown\": \"-15.23\",
          \"alpha\": \"2.34\",
          \"beta\": \"1.12\",
          \"benchmark_return\": \"10.11\"
      }

.. http:get:: /api/analytics/portfolio/{id}/performance/

   Get historical performance data.

.. http:get:: /api/analytics/portfolio/{id}/allocation/

   Get current asset allocation breakdown.

   **Response:**

   .. code-block:: json

      {
          \"allocations\": [
              {
                  \"asset_symbol\": \"AAPL\",
                  \"asset_name\": \"Apple Inc.\",
                  \"weight\": \"0.25\",
                  \"value\": \"31250.00\",
                  \"sector\": \"Technology\"
              }
          ],
          \"total_value\": \"125000.00\"
      }

Risk Analytics
~~~~~~~~~~~~~~

.. http:get:: /api/analytics/portfolio/{id}/risk/

   Get portfolio risk metrics.

   **Response:**

   .. code-block:: json

      {
          \"var_95\": \"-2345.67\",    // Value at Risk (95%)
          \"expected_shortfall\": \"-3456.78\",
          \"beta\": \"1.12\",
          \"correlation_spy\": \"0.85\",
          \"sector_concentration\": {
              \"Technology\": \"0.45\",
              \"Healthcare\": \"0.20\",
              \"Financials\": \"0.15\"
          }
      }

.. http:get:: /api/analytics/assets/{id}/technical/

   Get technical analysis indicators.

   **Query Parameters:**

   * ``indicators`` (array) - Indicators to calculate: ``sma_20``, ``rsi``, ``macd``
   * ``period`` (int) - Analysis period in days

Tax API
-------

Tax Calculations
~~~~~~~~~~~~~~~~

.. http:get:: /api/tax/analytics/summary/

   Get comprehensive tax summary.

   **Query Parameters:**

   * ``year`` (int) - Tax year
   * ``portfolio_id`` (int) - Specific portfolio filter

   **Response:**

   .. code-block:: json

      {
          \"tax_year\": 2024,
          \"capital_gains\": {
              \"short_term_gain_loss\": \"1250.00\",
              \"long_term_gain_loss\": \"3750.00\",
              \"net_capital_gain_loss\": \"5000.00\"
          },
          \"dividend_income\": {
              \"qualified_dividends\": \"850.00\",
              \"ordinary_dividends\": \"150.00\",
              \"total_dividends\": \"1000.00\"
          },
          \"estimated_tax_liability\": \"1200.00\"
      }

.. http:post:: /api/tax/analytics/calculate/

   Trigger tax calculations.

   **Request:**

   .. code-block:: json

      {
          \"year\": 2024,
          \"portfolio_id\": 1,
          \"reprocess\": false
      }

Tax Loss Harvesting
~~~~~~~~~~~~~~~~~~~

.. http:get:: /api/tax/loss-harvesting/

   List tax loss harvesting opportunities.

   **Response:**

   .. code-block:: json

      {
          \"opportunities\": [
              {
                  \"id\": 1,
                  \"position\": {
                      \"asset_symbol\": \"XOM\",
                      \"quantity\": \"100.00000000\",
                      \"average_cost\": \"85.50\",
                      \"current_price\": \"78.25\"
                  },
                  \"potential_loss_amount\": \"725.00\",
                  \"tax_benefit_estimate\": \"174.00\",
                  \"wash_sale_risk\": false,
                  \"recommendation\": \"Consider harvesting loss before year-end\"
              }
          ]
      }

.. http:post:: /api/tax/loss-harvesting/analyze/

   Analyze for new loss harvesting opportunities.

Tax Reports
~~~~~~~~~~~

.. http:get:: /api/tax/reports/

   List generated tax reports.

.. http:post:: /api/tax/reports/generate/

   Generate tax reports.

   **Request:**

   .. code-block:: json

      {
          \"year\": 2024,
          \"report_type\": \"all\"  // or \"schedule_d\", \"form_1099_div\"
      }

Real-time API
-------------

WebSocket Information
~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /realtime/websocket-info/

   Get WebSocket connection information.

   **Response:**

   .. code-block:: json

      {
          \"websocket_url\": \"ws://localhost:8000/ws/realtime/\",
          \"connection_info\": {
              \"protocol\": \"ws\",
              \"host\": \"localhost:8000\",
              \"path\": \"/ws/realtime/\",
              \"authentication\": \"session-based\"
          },
          \"message_types\": {
              \"ping\": \"Health check message\",
              \"subscribe_asset\": \"Subscribe to asset price updates\",
              \"subscribe_portfolio\": \"Subscribe to portfolio value updates\"
          }
      }

Service Status
~~~~~~~~~~~~~~

.. http:get:: /realtime/status/

   Get real-time service status and statistics.

   **Response:**

   .. code-block:: json

      {
          \"service_status\": \"running\",
          \"global_stats\": {
              \"total_connections\": 15,
              \"authenticated_users\": 8,
              \"portfolio_subscriptions\": 12,
              \"asset_subscriptions\": 25
          },
          \"user_stats\": {
              \"connection_count\": 2,
              \"subscriptions\": {
                  \"portfolios\": [123, 456],
                  \"assets\": [\"AAPL\", \"GOOGL\", \"MSFT\"]
              }
          }
      }

Force Updates
~~~~~~~~~~~~~

.. http:post:: /api/realtime/force_price_update/

   Force price update for specific assets.

   **Request:**

   .. code-block:: json

      {
          \"symbols\": [\"AAPL\", \"GOOGL\", \"MSFT\"]
      }

Error Handling
--------------

HTTP Status Codes
~~~~~~~~~~~~~~~~~~

* ``200 OK`` - Successful request
* ``201 Created`` - Resource created successfully
* ``204 No Content`` - Successful request with no response body
* ``400 Bad Request`` - Invalid request parameters
* ``401 Unauthorized`` - Authentication required
* ``403 Forbidden`` - Insufficient permissions
* ``404 Not Found`` - Resource not found
* ``429 Too Many Requests`` - Rate limit exceeded
* ``500 Internal Server Error`` - Server error

Error Response Format
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: json

   {
       \"error\": \"validation_error\",
       \"message\": \"Invalid portfolio ID\",
       \"details\": {
           \"field\": \"portfolio_id\",
           \"code\": \"invalid_choice\"
       }
   }

Rate Limiting
~~~~~~~~~~~~~

API endpoints are rate limited:

* **Authenticated users**: 1000 requests/hour
* **Anonymous users**: 100 requests/hour
* **Real-time endpoints**: 10 requests/minute

Rate limit headers:

.. code-block:: http

   X-RateLimit-Limit: 1000
   X-RateLimit-Remaining: 999
   X-RateLimit-Reset: 1640995200

API Client Examples
-------------------

Python Client
~~~~~~~~~~~~~~

.. code-block:: python

   import requests

   class FinanceAPIClient:
       def __init__(self, base_url, token):
           self.base_url = base_url
           self.headers = {'Authorization': f'Token {token}'}

       def get_portfolios(self):
           response = requests.get(
               f'{self.base_url}/api/portfolios/',
               headers=self.headers
           )
           return response.json()

       def create_transaction(self, transaction_data):
           response = requests.post(
               f'{self.base_url}/api/transactions/',
               json=transaction_data,
               headers=self.headers
           )
           return response.json()

       def run_backtest(self, strategy_id, backtest_config):
           # Create backtest
           backtest_data = {
               'strategy': strategy_id,
               **backtest_config
           }
           response = requests.post(
               f'{self.base_url}/api/backtesting/backtests/',
               json=backtest_data,
               headers=self.headers
           )
           backtest = response.json()

           # Run backtest
           response = requests.post(
               f'{self.base_url}/api/backtesting/backtests/{backtest[\"id\"]}/run/',
               headers=self.headers
           )
           return response.json()

JavaScript Client
~~~~~~~~~~~~~~~~~

.. code-block:: javascript

   class FinanceAPIClient {
       constructor(baseUrl, token) {
           this.baseUrl = baseUrl;
           this.headers = {
               'Authorization': `Token ${token}`,
               'Content-Type': 'application/json'
           };
       }

       async getPortfolios() {
           const response = await fetch(`${this.baseUrl}/api/portfolios/`, {
               headers: this.headers
           });
           return response.json();
       }

       async getPortfolioMetrics(portfolioId, period = '1y') {
           const response = await fetch(
               `${this.baseUrl}/api/analytics/portfolio/${portfolioId}/metrics/?period=${period}`,
               { headers: this.headers }
           );
           return response.json();
       }

       async createTransaction(transactionData) {
           const response = await fetch(`${this.baseUrl}/api/transactions/`, {
               method: 'POST',
               headers: this.headers,
               body: JSON.stringify(transactionData)
           });
           return response.json();
       }
   }

See Also
--------

* :doc:`websocket` - WebSocket API reference
* :doc:`authentication` - Authentication and authorization details
* :doc:`python_api` - Internal Python API reference
* :doc:`../development/testing` - API testing guidelines
