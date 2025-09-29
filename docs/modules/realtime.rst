Real-time Data Streaming
========================

Comprehensive real-time WebSocket implementation reference for live market data and portfolio tracking.

.. currentmodule:: personal_finance.realtime

.. contents:: Table of Contents
   :local:
   :depth: 3

Module Overview
---------------

The Real-time module provides WebSocket-based live data streaming capabilities:

.. toctree::
   :maxdepth: 2

   Services <services/realtime>
   Consumers <consumers/realtime>
   Connections <connections/realtime>
   Tasks <tasks/realtime>

Core Features
~~~~~~~~~~~~~

- **Live Price Feeds**: Real-time asset price updates from multiple data sources
- **Portfolio Tracking**: Live portfolio value calculations with position updates
- **WebSocket Management**: Connection handling, authentication, and message routing
- **Scalable Architecture**: High-frequency updates for multiple concurrent users
- **Production Ready**: Comprehensive error handling, logging, and monitoring

WebSocket Architecture
----------------------

Connection Management
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: personal_finance.realtime.connection_manager.ConnectionManager
   :members:
   :undoc-members:
   :show-inheritance:

The connection manager handles all WebSocket connections, user authentication, and subscription management:

.. code-block:: python

   from personal_finance.realtime.connection_manager import ConnectionManager
   from personal_finance.realtime.consumers import RealtimeConsumer

   # Get the global connection manager instance
   connection_manager = ConnectionManager()

   # Connection stats
   print(f\"Total connections: {connection_manager.get_connection_count()}\")
   print(f\"Authenticated users: {connection_manager.get_authenticated_user_count()}\")

   # User-specific connections
   user_connections = connection_manager.get_user_connections(user)
   print(f\"User has {len(user_connections)} active connections\")

   # Broadcast to all user connections
   connection_manager.broadcast_to_user(user, {
       'type': 'notification',
       'data': {'message': 'Portfolio updated successfully'}
   })

   # Broadcast to specific subscribers
   connection_manager.broadcast_to_asset_subscribers('AAPL', {
       'type': 'asset_update',
       'data': {'symbol': 'AAPL', 'price': 150.25, 'change': 2.50}
   })

WebSocket Consumer
~~~~~~~~~~~~~~~~~~

.. autoclass:: personal_finance.realtime.consumers.RealtimeConsumer
   :members:
   :undoc-members:

Main WebSocket consumer handling client connections and message routing:

.. code-block:: python

   # RealtimeConsumer handles all WebSocket connections
   class RealtimeConsumer(AsyncWebsocketConsumer):
       \"\"\"Real-time WebSocket consumer for live data streaming.\"\"\"

       async def connect(self):
           \"\"\"Handle new WebSocket connection.\"\"\"
           # Authenticate user
           user = self.scope.get('user')
           if not user or not user.is_authenticated:
               await self.close()
               return

           # Register connection
           await self.connection_manager.add_connection(self)
           await self.accept()

           # Send connection confirmation
           await self.send_json({
               'type': 'connection',
               'data': {
                   'status': 'connected',
                   'connection_id': str(self.connection_id),
                   'authenticated': True,
                   'user_id': user.id
               }
           })

Message Protocol
~~~~~~~~~~~~~~~~

All WebSocket messages follow a standardized JSON protocol:

**Base Message Structure:**

.. code-block:: json

   {
       \"type\": \"message_type\",
       \"data\": {
           // Message-specific payload
       },
       \"timestamp\": \"2024-01-15T10:30:00Z\",
       \"connection_id\": \"uuid-string\"
   }

**Client to Server Messages:**

.. code-block:: javascript

   // Ping/Pong for connection health
   {
       \"type\": \"ping\",
       \"data\": {}
   }

   // Subscribe to asset price updates
   {
       \"type\": \"subscribe_asset\",
       \"data\": {
           \"symbol\": \"AAPL\"
       }
   }

   // Subscribe to portfolio updates
   {
       \"type\": \"subscribe_portfolio\",
       \"data\": {
           \"portfolio_id\": 123
       }
   }

   // Unsubscribe from updates
   {
       \"type\": \"unsubscribe_asset\",
       \"data\": {
           \"symbol\": \"AAPL\"
       }
   }

**Server to Client Messages:**

.. code-block:: json

   // Asset price update
   {
       \"type\": \"asset_update\",
       \"data\": {
           \"symbol\": \"AAPL\",
           \"price\": 150.25,
           \"change\": 2.50,
           \"change_percent\": 1.69,
           \"volume\": 50000000,
           \"high\": 151.00,
           \"low\": 148.50,
           \"market_cap\": 2400000000000,
           \"last_updated\": \"2024-01-15T15:30:00Z\"
       }
   }

   // Portfolio value update
   {
       \"type\": \"portfolio_update\",
       \"data\": {
           \"portfolio_id\": 123,
           \"name\": \"Growth Portfolio\",
           \"total_value\": 50000.00,
           \"daily_change\": 125.50,
           \"daily_change_percent\": 0.25,
           \"positions_updated\": [
               {
                   \"symbol\": \"AAPL\",
                   \"quantity\": 100,
                   \"current_value\": 15025.00,
                   \"daily_change\": 250.00
               }
           ]
       }
   }

Price Feed Service
------------------

Real-time Price Updates
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: personal_finance.realtime.services.PriceFeedService
   :members:
   :undoc-members:

Core service managing real-time price data updates:

.. code-block:: python

   from personal_finance.realtime.services import PriceFeedService
   from decimal import Decimal

   # Initialize the price feed service
   price_service = PriceFeedService(
       update_interval=30,  # Update every 30 seconds
       batch_size=50,       # Process 50 assets per batch
       enable_caching=True  # Enable Redis caching
   )

   # Start the price feed (blocking operation)
   price_service.start_price_feed()

   # Update specific assets manually
   symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
   updated_prices = price_service.update_asset_prices(symbols)

   for symbol, price_data in updated_prices.items():
       print(f\"{symbol}: ${price_data['price']} ({price_data['change']:+.2f})\")

   # Get current service status
   status = price_service.get_service_status()
   print(f\"Service running: {status['running']}\")
   print(f\"Last update: {status['last_update']}\")
   print(f\"Assets tracked: {status['assets_tracked']}\")
   print(f\"Update frequency: {status['update_interval']}s\")

Batch Processing
~~~~~~~~~~~~~~~~

Efficient batch processing for high-volume price updates:

.. code-block:: python

   from personal_finance.realtime.batch import BatchPriceProcessor

   # Initialize batch processor
   batch_processor = BatchPriceProcessor(
       batch_size=100,
       concurrent_batches=3,
       retry_failed=True
   )

   # Process large asset list efficiently
   all_tracked_symbols = Asset.objects.filter(
       is_active=True,
       positions__quantity__gt=0
   ).values_list('symbol', flat=True).distinct()

   print(f\"Processing {len(all_tracked_symbols)} assets in batches...\")

   # Process with progress tracking
   for batch_num, results in batch_processor.process_in_batches(all_tracked_symbols):
       successful = len([r for r in results if r['success']])
       print(f\"Batch {batch_num}: {successful}/{len(results)} successful\")

   # Handle failed updates
   failed_updates = batch_processor.get_failed_updates()
   if failed_updates:
       print(f\"Retrying {len(failed_updates)} failed updates...\")
       retry_results = batch_processor.retry_failed_updates(failed_updates)

Data Source Integration
~~~~~~~~~~~~~~~~~~~~~~~

Multiple market data source integration:

.. code-block:: python

   from personal_finance.realtime.data_sources import (
       YahooFinanceSource,
       AlphaVantageSource,
       DataSourceManager
   )

   # Configure data sources with fallback
   data_source_manager = DataSourceManager()

   # Primary source
   yahoo_source = YahooFinanceSource(
       api_key=settings.YAHOO_FINANCE_API_KEY,
       rate_limit=100  # requests per minute
   )
   data_source_manager.add_source(yahoo_source, priority=1)

   # Fallback source
   alpha_vantage_source = AlphaVantageSource(
       api_key=settings.ALPHA_VANTAGE_API_KEY,
       rate_limit=5  # requests per minute (free tier)
   )
   data_source_manager.add_source(alpha_vantage_source, priority=2)

   # Fetch data with automatic fallback
   price_data = data_source_manager.get_asset_data(['AAPL', 'GOOGL'])

   for symbol, data in price_data.items():
       if data['success']:
           print(f\"{symbol}: ${data['price']} (source: {data['source']})\")
       else:
           print(f\"{symbol}: Failed - {data['error']}\")

Portfolio Value Tracking
------------------------

Real-time Portfolio Updates
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: personal_finance.realtime.portfolio_tracker.PortfolioTracker
   :members:
   :undoc-members:

Service for real-time portfolio value calculations and updates:

.. code-block:: python

   from personal_finance.realtime.portfolio_tracker import PortfolioTracker

   # Initialize portfolio tracker
   tracker = PortfolioTracker()

   # Get user's portfolios for real-time tracking
   user_portfolios = Portfolio.objects.filter(user=user)

   # Start tracking all user portfolios
   for portfolio in user_portfolios:
       tracker.start_tracking_portfolio(portfolio)

   # Update specific portfolio based on price changes
   portfolio = user_portfolios.first()
   price_updates = {
       'AAPL': Decimal('150.25'),
       'GOOGL': Decimal('2800.75'),
       'MSFT': Decimal('420.30')
   }

   updated_portfolio = tracker.update_portfolio_values(portfolio, price_updates)

   print(f\"Portfolio '{portfolio.name}' updated:\")
   print(f\"  Total value: ${updated_portfolio['total_value']}\")
   print(f\"  Daily change: ${updated_portfolio['daily_change']} ({updated_portfolio['daily_change_percent']:.2f}%)\")

   # Broadcast updates to WebSocket subscribers
   if updated_portfolio['value_changed']:
       connection_manager.broadcast_to_portfolio_subscribers(
           portfolio.id,
           {
               'type': 'portfolio_update',
               'data': updated_portfolio
           }
       )

Position-Level Updates
~~~~~~~~~~~~~~~~~~~~~~

Track individual position changes within portfolios:

.. code-block:: python

   # Update individual positions and propagate to portfolio
   position = Position.objects.get(portfolio=portfolio, asset__symbol='AAPL')

   position_update = tracker.update_position_value(
       position,
       new_price=Decimal('150.25')
   )

   print(f\"Position update for {position.asset.symbol}:\")
   print(f\"  Quantity: {position.quantity}\")
   print(f\"  New price: ${position_update['current_price']}\")
   print(f\"  Position value: ${position_update['current_value']}\")
   print(f\"  Daily change: ${position_update['daily_change']}\")
   print(f\"  Total return: ${position_update['total_return']} ({position_update['total_return_percent']:.2f}%)\")

   # Send position-specific updates to subscribers
   if position_update['significant_change']:  # > 1% change
       connection_manager.broadcast_to_user(
           portfolio.user,
           {
               'type': 'position_update',
               'data': position_update
           }
       )

Client-Side Integration
-----------------------

JavaScript WebSocket Client
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Comprehensive JavaScript client for real-time data consumption:

.. code-block:: javascript

   class PersonalFinanceWebSocket {
       constructor(options = {}) {
           this.url = options.url || 'ws://localhost:8000/ws/realtime/';
           this.reconnectInterval = options.reconnectInterval || 5000;
           this.maxReconnectAttempts = options.maxReconnectAttempts || 10;
           this.reconnectAttempts = 0;

           this.socket = null;
           this.isConnected = false;
           this.subscriptions = new Set();
           this.messageHandlers = new Map();
           this.connectionId = null;

           // Event callbacks
           this.onConnect = options.onConnect || (() => {});
           this.onDisconnect = options.onDisconnect || (() => {});
           this.onError = options.onError || console.error;
           this.onMessage = options.onMessage || (() => {});
       }

       connect() {
           try {
               this.socket = new WebSocket(this.url);
               this.setupEventHandlers();
           } catch (error) {
               this.onError('WebSocket connection failed:', error);
               this.scheduleReconnect();
           }
       }

       setupEventHandlers() {
           this.socket.onopen = (event) => {
               console.log('WebSocket connected');
               this.isConnected = true;
               this.reconnectAttempts = 0;

               // Send ping to establish connection
               this.sendMessage('ping', {});
               this.onConnect(event);
           };

           this.socket.onmessage = (event) => {
               try {
                   const message = JSON.parse(event.data);
                   this.handleMessage(message);
               } catch (error) {
                   this.onError('Failed to parse WebSocket message:', error);
               }
           };

           this.socket.onclose = (event) => {
               console.log('WebSocket disconnected');
               this.isConnected = false;
               this.connectionId = null;
               this.onDisconnect(event);

               if (!event.wasClean) {
                   this.scheduleReconnect();
               }
           };

           this.socket.onerror = (error) => {
               console.error('WebSocket error:', error);
               this.onError(error);
           };
       }

       sendMessage(type, data) {
           if (!this.isConnected || !this.socket) {
               console.warn('WebSocket not connected, cannot send message');
               return false;
           }

           const message = {
               type: type,
               data: data,
               timestamp: new Date().toISOString()
           };

           this.socket.send(JSON.stringify(message));
           return true;
       }

       handleMessage(message) {
           // Handle built-in message types
           switch (message.type) {
               case 'connection':
                   this.connectionId = message.data.connection_id;
                   break;

               case 'pong':
                   console.log('Received pong from server');
                   break;

               case 'asset_update':
                   this.handleAssetUpdate(message.data);
                   break;

               case 'portfolio_update':
                   this.handlePortfolioUpdate(message.data);
                   break;

               case 'error':
                   this.onError('Server error:', message.data);
                   break;
           }

           // Call registered message handlers
           if (this.messageHandlers.has(message.type)) {
               const handler = this.messageHandlers.get(message.type);
               handler(message.data, message);
           }

           // Call general message callback
           this.onMessage(message);
       }

       // Asset subscription management
       subscribeToAsset(symbol) {
           if (this.sendMessage('subscribe_asset', { symbol: symbol })) {
               this.subscriptions.add(`asset:${symbol}`);
               return true;
           }
           return false;
       }

       unsubscribeFromAsset(symbol) {
           if (this.sendMessage('unsubscribe_asset', { symbol: symbol })) {
               this.subscriptions.delete(`asset:${symbol}`);
               return true;
           }
           return false;
       }

       // Portfolio subscription management
       subscribeToPortfolio(portfolioId) {
           if (this.sendMessage('subscribe_portfolio', { portfolio_id: portfolioId })) {
               this.subscriptions.add(`portfolio:${portfolioId}`);
               return true;
           }
           return false;
       }

       unsubscribeFromPortfolio(portfolioId) {
           if (this.sendMessage('unsubscribe_portfolio', { portfolio_id: portfolioId })) {
               this.subscriptions.delete(`portfolio:${portfolioId}`);
               return true;
           }
           return false;
       }

       // Message handler registration
       onMessageType(type, handler) {
           this.messageHandlers.set(type, handler);
       }

       // Built-in update handlers
       handleAssetUpdate(data) {
           console.log(`Asset update: ${data.symbol} = $${data.price}`);

           // Update DOM elements
           const priceElement = document.getElementById(`price-${data.symbol}`);
           if (priceElement) {
               priceElement.textContent = `$${data.price.toFixed(2)}`;

               // Add visual feedback for price changes
               const changeClass = data.change >= 0 ? 'price-up' : 'price-down';
               priceElement.className = `price ${changeClass}`;
           }

           const changeElement = document.getElementById(`change-${data.symbol}`);
           if (changeElement) {
               changeElement.textContent = `${data.change >= 0 ? '+' : ''}${data.change.toFixed(2)} (${data.change_percent.toFixed(2)}%)`;
           }
       }

       handlePortfolioUpdate(data) {
           console.log(`Portfolio update: ${data.name} = $${data.total_value}`);

           // Update portfolio display
           const valueElement = document.getElementById(`portfolio-value-${data.portfolio_id}`);
           if (valueElement) {
               valueElement.textContent = `$${data.total_value.toFixed(2)}`;
           }

           const changeElement = document.getElementById(`portfolio-change-${data.portfolio_id}`);
           if (changeElement) {
               const changeText = `${data.daily_change >= 0 ? '+' : ''}$${data.daily_change.toFixed(2)} (${data.daily_change_percent.toFixed(2)}%)`;
               changeElement.textContent = changeText;
               changeElement.className = data.daily_change >= 0 ? 'change-positive' : 'change-negative';
           }
       }

       // Connection management
       scheduleReconnect() {
           if (this.reconnectAttempts >= this.maxReconnectAttempts) {
               console.error('Max reconnection attempts reached');
               return;
           }

           this.reconnectAttempts++;
           console.log(`Scheduling reconnection attempt ${this.reconnectAttempts} in ${this.reconnectInterval}ms`);

           setTimeout(() => {
               console.log('Attempting to reconnect...');
               this.connect();
           }, this.reconnectInterval);
       }

       disconnect() {
           if (this.socket) {
               this.socket.close();
           }
       }
   }

   // Usage example
   const wsClient = new PersonalFinanceWebSocket({
       url: 'ws://localhost:8000/ws/realtime/',
       onConnect: () => console.log('Connected to real-time feed'),
       onDisconnect: () => console.log('Disconnected from real-time feed'),
       onError: (error) => console.error('WebSocket error:', error)
   });

   // Connect and subscribe
   wsClient.connect();

   // Subscribe to specific assets
   wsClient.subscribeToAsset('AAPL');
   wsClient.subscribeToAsset('GOOGL');

   // Subscribe to portfolio updates
   wsClient.subscribeToPortfolio(123);

   // Register custom message handlers
   wsClient.onMessageType('custom_alert', (data) => {
       alert(`Custom alert: ${data.message}`);
   });

React Integration
~~~~~~~~~~~~~~~~~

React hook for WebSocket integration:

.. code-block:: jsx

   import { useState, useEffect, useRef, useCallback } from 'react';

   // Custom hook for WebSocket connection
   function usePersonalFinanceWebSocket(url, options = {}) {
       const [isConnected, setIsConnected] = useState(false);
       const [lastMessage, setLastMessage] = useState(null);
       const [connectionError, setConnectionError] = useState(null);
       const [assetPrices, setAssetPrices] = useState({});
       const [portfolioValues, setPortfolioValues] = useState({});

       const wsClient = useRef(null);
       const subscriptions = useRef(new Set());

       useEffect(() => {
           // Initialize WebSocket client
           wsClient.current = new PersonalFinanceWebSocket({
               url,
               onConnect: () => {
                   setIsConnected(true);
                   setConnectionError(null);
               },
               onDisconnect: () => {
                   setIsConnected(false);
               },
               onError: (error) => {
                   setConnectionError(error);
               },
               onMessage: (message) => {
                   setLastMessage(message);
               }
           });

           // Register message handlers
           wsClient.current.onMessageType('asset_update', (data) => {
               setAssetPrices(prev => ({
                   ...prev,
                   [data.symbol]: data
               }));
           });

           wsClient.current.onMessageType('portfolio_update', (data) => {
               setPortfolioValues(prev => ({
                   ...prev,
                   [data.portfolio_id]: data
               }));
           });

           // Connect
           wsClient.current.connect();

           // Cleanup on unmount
           return () => {
               wsClient.current.disconnect();
           };
       }, [url]);

       const subscribeToAsset = useCallback((symbol) => {
           if (wsClient.current && !subscriptions.current.has(`asset:${symbol}`)) {
               wsClient.current.subscribeToAsset(symbol);
               subscriptions.current.add(`asset:${symbol}`);
           }
       }, []);

       const subscribeToPortfolio = useCallback((portfolioId) => {
           if (wsClient.current && !subscriptions.current.has(`portfolio:${portfolioId}`)) {
               wsClient.current.subscribeToPortfolio(portfolioId);
               subscriptions.current.add(`portfolio:${portfolioId}`);
           }
       }, []);

       const unsubscribeFromAsset = useCallback((symbol) => {
           if (wsClient.current && subscriptions.current.has(`asset:${symbol}`)) {
               wsClient.current.unsubscribeFromAsset(symbol);
               subscriptions.current.delete(`asset:${symbol}`);
           }
       }, []);

       return {
           isConnected,
           lastMessage,
           connectionError,
           assetPrices,
           portfolioValues,
           subscribeToAsset,
           subscribeToPortfolio,
           unsubscribeFromAsset,
           sendMessage: wsClient.current?.sendMessage.bind(wsClient.current)
       };
   }

   // Portfolio component using the hook
   function PortfolioTracker({ portfolioId, watchlist = [] }) {
       const {
           isConnected,
           assetPrices,
           portfolioValues,
           subscribeToAsset,
           subscribeToPortfolio
       } = usePersonalFinanceWebSocket('ws://localhost:8000/ws/realtime/');

       useEffect(() => {
           if (isConnected) {
               // Subscribe to portfolio updates
               subscribeToPortfolio(portfolioId);

               // Subscribe to watchlist assets
               watchlist.forEach(symbol => {
                   subscribeToAsset(symbol);
               });
           }
       }, [isConnected, portfolioId, watchlist, subscribeToAsset, subscribeToPortfolio]);

       const portfolioData = portfolioValues[portfolioId];

       return (
           <div className=\"portfolio-tracker\">
               <div className=\"connection-status\">
                   Status: {isConnected ?
                       <span className=\"connected\">Connected</span> :
                       <span className=\"disconnected\">Disconnected</span>
                   }
               </div>

               {portfolioData && (
                   <div className=\"portfolio-summary\">
                       <h2>{portfolioData.name}</h2>
                       <div className=\"portfolio-value\">
                           ${portfolioData.total_value.toFixed(2)}
                       </div>
                       <div className={`portfolio-change ${portfolioData.daily_change >= 0 ? 'positive' : 'negative'}`}>
                           {portfolioData.daily_change >= 0 ? '+' : ''}
                           ${portfolioData.daily_change.toFixed(2)}
                           ({portfolioData.daily_change_percent.toFixed(2)}%)
                       </div>
                   </div>
               )}

               <div className=\"watchlist\">
                   <h3>Watchlist</h3>
                   {watchlist.map(symbol => {
                       const priceData = assetPrices[symbol];
                       return (
                           <div key={symbol} className=\"watchlist-item\">
                               <span className=\"symbol\">{symbol}</span>
                               {priceData ? (
                                   <>
                                       <span className=\"price\">${priceData.price.toFixed(2)}</span>
                                       <span className={`change ${priceData.change >= 0 ? 'positive' : 'negative'}`}>
                                           {priceData.change >= 0 ? '+' : ''}{priceData.change.toFixed(2)}
                                           ({priceData.change_percent.toFixed(2)}%)
                                       </span>
                                   </>
                               ) : (
                                   <span className=\"loading\">Loading...</span>
                               )}
                           </div>
                       );
                   })}
               </div>
           </div>
       );
   }

REST API Integration
--------------------

WebSocket Status Endpoints
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Get WebSocket Connection Information**

.. http:get:: /api/v1/realtime/websocket-info/

   Retrieve WebSocket connection details and capabilities.

   **Example Response:**

   .. code-block:: json

      {
        \"websocket_url\": \"ws://localhost:8000/ws/realtime/\",
        \"secure_websocket_url\": \"wss://yourfinance.com/ws/realtime/\",
        \"connection_info\": {
          \"protocol\": \"ws\",
          \"host\": \"localhost:8000\",
          \"path\": \"/ws/realtime/\",
          \"authentication\": \"session-based\",
          \"max_connections_per_user\": 5,
          \"message_size_limit\": 1024
        },
        \"supported_message_types\": {
          \"ping\": \"Health check message\",
          \"subscribe_asset\": \"Subscribe to asset price updates\",
          \"subscribe_portfolio\": \"Subscribe to portfolio value updates\",
          \"unsubscribe_asset\": \"Unsubscribe from asset updates\",
          \"unsubscribe_portfolio\": \"Unsubscribe from portfolio updates\"
        },
        \"rate_limits\": {
          \"messages_per_minute\": 60,
          \"subscriptions_per_connection\": 50
        }
      }

**Get Real-time Service Status**

.. http:get:: /api/v1/realtime/status/

   Check real-time service status and connection statistics.

   **Example Response:**

   .. code-block:: json

      {
        \"service_status\": \"running\",
        \"price_feed_active\": true,
        \"last_price_update\": \"2024-01-15T15:30:00Z\",
        \"global_stats\": {
          \"total_connections\": 25,
          \"authenticated_users\": 15,
          \"total_asset_subscriptions\": 150,
          \"total_portfolio_subscriptions\": 35,
          \"active_assets_tracked\": 85
        },
        \"user_stats\": {
          \"connection_count\": 2,
          \"subscriptions\": {
            \"assets\": [\"AAPL\", \"GOOGL\", \"MSFT\", \"AMZN\"],
            \"portfolios\": [123, 456]
          },
          \"last_activity\": \"2024-01-15T15:29:45Z\"
        },
        \"performance_metrics\": {
          \"average_message_latency_ms\": 25,
          \"messages_per_second\": 150,
          \"update_frequency_seconds\": 30
        }
      }

Price Update Endpoints
~~~~~~~~~~~~~~~~~~~~~~

**Force Price Update**

.. http:post:: /api/v1/realtime/force-price-update/

   Manually trigger price updates for specific assets.

   **Request Body:**

   .. code-block:: json

      {
        \"symbols\": [\"AAPL\", \"GOOGL\", \"MSFT\"],
        \"broadcast\": true,
        \"update_historical\": false
      }

   **Example Response:**

   .. code-block:: json

      {
        \"status\": \"success\",
        \"updated_count\": 3,
        \"failed_count\": 0,
        \"results\": {
          \"AAPL\": {
            \"success\": true,
            \"old_price\": 147.75,
            \"new_price\": 150.25,
            \"change\": 2.50,
            \"last_updated\": \"2024-01-15T15:35:00Z\"
          },
          \"GOOGL\": {
            \"success\": true,
            \"old_price\": 2750.25,
            \"new_price\": 2800.75,
            \"change\": 50.50,
            \"last_updated\": \"2024-01-15T15:35:01Z\"
          },
          \"MSFT\": {
            \"success\": true,
            \"old_price\": 418.30,
            \"new_price\": 420.30,
            \"change\": 2.00,
            \"last_updated\": \"2024-01-15T15:35:02Z\"
          }
        },
        \"broadcast_sent\": true,
        \"subscribers_notified\": 12
      }

**Get Price History**

.. http:get:: /api/v1/realtime/price-history/

   Retrieve recent price history for assets.

   **Query Parameters:**

   - **symbols** (string) -- Comma-separated list of asset symbols
   - **hours** (integer) -- Hours of history to retrieve (default: 24)
   - **resolution** (string) -- Time resolution: ``1m``, ``5m``, ``15m``, ``1h`` (default: 5m)

   **Example Response:**

   .. code-block:: json

      {
        \"AAPL\": {
          \"symbol\": \"AAPL\",
          \"resolution\": \"5m\",
          \"data_points\": 288,
          \"price_history\": [
            {
              \"timestamp\": \"2024-01-15T09:30:00Z\",
              \"price\": 148.50,
              \"volume\": 1200000
            },
            {
              \"timestamp\": \"2024-01-15T09:35:00Z\",
              \"price\": 149.25,
              \"volume\": 980000
            }
          ],
          \"statistics\": {
            \"min_price\": 147.25,
            \"max_price\": 151.00,
            \"avg_price\": 149.12,
            \"total_volume\": 45600000
          }
        }
      }

Management Commands
-------------------

Start Price Feed Service
~~~~~~~~~~~~~~~~~~~~~~~~

Start the real-time price feed service:

.. code-block:: bash

   # Basic usage - start with default settings
   python manage.py start_price_feed

   # Custom configuration
   python manage.py start_price_feed \\
       --interval 15 \\           # Update every 15 seconds
       --batch-size 100 \\        # Process 100 assets per batch
       --max-workers 4 \\         # Use 4 parallel workers
       --verbose                  # Enable detailed logging

   # Production deployment with background execution
   nohup python manage.py start_price_feed \\
       --interval 30 \\
       --batch-size 50 \\
       > /var/log/price_feed.log 2>&1 &

**Command Options:**

+-------------------+------------------------------------------+
| Option            | Description                              |
+===================+==========================================+
| ``--interval``    | Update interval in seconds (default: 30)|
+-------------------+------------------------------------------+
| ``--batch-size``  | Assets processed per batch (default: 50)|
+-------------------+------------------------------------------+
| ``--max-workers`` | Number of parallel workers (default: 2) |
+-------------------+------------------------------------------+
| ``--symbols``     | Specific symbols to track (optional)    |
+-------------------+------------------------------------------+
| ``--verbose``     | Enable detailed logging output          |
+-------------------+------------------------------------------+
| ``--dry-run``     | Test mode without actual updates        |
+-------------------+------------------------------------------+

Update Asset Prices (Manual)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Perform one-time price updates:

.. code-block:: bash

   # Update all tracked assets
   python manage.py update_asset_prices

   # Update specific symbols
   python manage.py update_asset_prices --symbols AAPL MSFT GOOGL AMZN TSLA

   # Update with historical data refresh
   python manage.py update_asset_prices --historical --days 7

   # Update and broadcast to WebSocket subscribers
   python manage.py update_asset_prices --broadcast

   # Dry run to test without making changes
   python manage.py update_asset_prices --dry-run --verbose

Monitor WebSocket Connections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Monitor active WebSocket connections:

.. code-block:: bash

   # Show connection statistics
   python manage.py monitor_websockets

   # Show detailed connection information
   python manage.py monitor_websockets --detailed

   # Monitor specific user
   python manage.py monitor_websockets --user admin

   # Export connection statistics
   python manage.py monitor_websockets --export /tmp/websocket_stats.json

Configuration
-------------

Django Settings
~~~~~~~~~~~~~~~

Add real-time configuration to your Django settings:

.. code-block:: python

   # config/settings/base.py

   # Real-time WebSocket Settings
   REALTIME_UPDATE_INTERVAL = env.int('REALTIME_UPDATE_INTERVAL', 30)  # seconds
   REALTIME_BATCH_SIZE = env.int('REALTIME_BATCH_SIZE', 50)           # assets per batch
   REALTIME_CACHE_TIMEOUT = env.int('REALTIME_CACHE_TIMEOUT', 300)    # 5 minutes
   REALTIME_MAX_WORKERS = env.int('REALTIME_MAX_WORKERS', 2)          # parallel workers

   # WebSocket Settings
   WEBSOCKET_TIMEOUT = env.int('WEBSOCKET_TIMEOUT', 300)              # 5 minutes
   WEBSOCKET_MAX_CONNECTIONS_PER_USER = env.int('WEBSOCKET_MAX_CONNECTIONS_PER_USER', 5)
   WEBSOCKET_MAX_SUBSCRIPTIONS_PER_CONNECTION = env.int('WEBSOCKET_MAX_SUBSCRIPTIONS_PER_CONNECTION', 50)
   WEBSOCKET_MESSAGE_SIZE_LIMIT = env.int('WEBSOCKET_MESSAGE_SIZE_LIMIT', 1024)  # bytes
   WEBSOCKET_RATE_LIMIT_MESSAGES_PER_MINUTE = env.int('WEBSOCKET_RATE_LIMIT_MESSAGES_PER_MINUTE', 60)

   # Market Data Sources
   MARKET_DATA_SOURCE_PRIORITIES = {
       'yahoo_finance': 1,      # Primary source
       'alpha_vantage': 2,      # Fallback source
       'iex_cloud': 3,          # Secondary fallback
   }

   # Redis Configuration for WebSocket (if using Redis)
   CHANNEL_LAYERS = {
       'default': {
           'BACKEND': 'channels_redis.core.RedisChannelLayer',
           'CONFIG': {
               'hosts': [env('REDIS_URL', 'redis://localhost:6379/3')],
               'capacity': 1500,
               'expiry': 60,
           },
       },
   }

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # .env file for real-time configuration

   # Price Update Settings
   REALTIME_UPDATE_INTERVAL=30
   REALTIME_BATCH_SIZE=50
   REALTIME_CACHE_TIMEOUT=300
   REALTIME_MAX_WORKERS=2

   # WebSocket Configuration
   WEBSOCKET_TIMEOUT=300
   WEBSOCKET_MAX_CONNECTIONS_PER_USER=5
   WEBSOCKET_MAX_SUBSCRIPTIONS_PER_CONNECTION=50
   WEBSOCKET_MESSAGE_SIZE_LIMIT=1024
   WEBSOCKET_RATE_LIMIT_MESSAGES_PER_MINUTE=60

   # Market Data API Keys
   YAHOO_FINANCE_API_KEY=your-yahoo-finance-api-key
   ALPHA_VANTAGE_API_KEY=your-alpha-vantage-api-key
   IEX_CLOUD_API_KEY=your-iex-cloud-api-key

   # Redis for WebSocket channels (optional)
   REDIS_WEBSOCKET_URL=redis://localhost:6379/3

Production Deployment
---------------------

Docker Configuration
~~~~~~~~~~~~~~~~~~~~

Configure Docker for WebSocket support:

.. code-block:: dockerfile

   # Dockerfile - Add WebSocket support
   FROM python:3.11-slim

   # Install system dependencies
   RUN apt-get update && apt-get install -y \\
       build-essential \\
       && rm -rf /var/lib/apt/lists/*

   # Set working directory
   WORKDIR /app

   # Copy requirements and install Python dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   # Copy application code
   COPY . .

   # Expose ports
   EXPOSE 8000

   # Command for WebSocket-enabled server
   CMD [\"daphne\", \"-b\", \"0.0.0.0\", \"-p\", \"8000\", \"config.asgi:application\"]

.. code-block:: yaml

   # docker-compose.yml - Real-time services
   version: '3.8'

   services:
     web:
       build: .
       ports:
         - \"8000:8000\"
       environment:
         - DJANGO_SETTINGS_MODULE=config.settings.production
         - REALTIME_UPDATE_INTERVAL=30
         - WEBSOCKET_TIMEOUT=300
       depends_on:
         - redis
         - db

     redis:
       image: redis:7-alpine
       ports:
         - \"6379:6379\"
       volumes:
         - redis_data:/data

     price-feed:
       build: .
       command: python manage.py start_price_feed --interval 30 --batch-size 50
       environment:
         - DJANGO_SETTINGS_MODULE=config.settings.production
       depends_on:
         - redis
         - db

   volumes:
     redis_data:

Nginx Configuration
~~~~~~~~~~~~~~~~~~

Configure Nginx for WebSocket proxying:

.. code-block:: nginx

   # nginx.conf - WebSocket proxy configuration
   upstream django_app {
       server web:8000;
   }

   server {
       listen 80;
       server_name yourfinance.com;

       # Regular HTTP traffic
       location / {
           proxy_pass http://django_app;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       # WebSocket traffic
       location /ws/ {
           proxy_pass http://django_app;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection \"upgrade\";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;

           # WebSocket specific settings
           proxy_read_timeout 86400s;
           proxy_send_timeout 86400s;
           proxy_connect_timeout 60s;
       }
   }

Systemd Service Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configure systemd service for price feed:

.. code-block:: ini

   # /etc/systemd/system/personal-finance-price-feed.service
   [Unit]
   Description=Personal Finance Price Feed Service
   After=network.target redis.service postgresql.service
   Requires=redis.service postgresql.service

   [Service]
   Type=simple
   User=finance
   Group=finance
   WorkingDirectory=/opt/personal-finance
   Environment=DJANGO_SETTINGS_MODULE=config.settings.production
   Environment=PATH=/opt/personal-finance/venv/bin:/usr/bin:/bin
   ExecStart=/opt/personal-finance/venv/bin/python manage.py start_price_feed --interval 30 --batch-size 50
   ExecReload=/bin/kill -HUP $MAINPID
   Restart=always
   RestartSec=5
   StandardOutput=journal
   StandardError=journal
   SyslogIdentifier=price-feed

   [Install]
   WantedBy=multi-user.target

.. code-block:: bash

   # Enable and start the service
   sudo systemctl daemon-reload
   sudo systemctl enable personal-finance-price-feed
   sudo systemctl start personal-finance-price-feed

   # Check service status
   sudo systemctl status personal-finance-price-feed

   # View logs
   sudo journalctl -u personal-finance-price-feed -f

Monitoring and Logging
----------------------

Health Check Endpoints
~~~~~~~~~~~~~~~~~~~~~~

Implement comprehensive health checks:

.. code-block:: python

   # realtime/views.py
   from django.http import JsonResponse
   from django.utils import timezone
   from .services import PriceFeedService
   from .connection_manager import ConnectionManager

   def health_check(request):
       \"\"\"Comprehensive health check for real-time services.\"\"\"
       price_service = PriceFeedService()
       connection_manager = ConnectionManager()

       # Check service status
       price_feed_status = price_service.get_service_status()

       # Check WebSocket connections
       connection_stats = {
           'total_connections': connection_manager.get_connection_count(),
           'authenticated_users': connection_manager.get_authenticated_user_count(),
           'asset_subscriptions': connection_manager.get_total_asset_subscriptions(),
           'portfolio_subscriptions': connection_manager.get_total_portfolio_subscriptions()
       }

       # Check data freshness
       from .models import AssetPrice
       latest_price_update = AssetPrice.objects.order_by('-last_updated').first()

       data_freshness = None
       if latest_price_update:
           time_since_update = (timezone.now() - latest_price_update.last_updated).total_seconds()
           data_freshness = {
               'last_update': latest_price_update.last_updated.isoformat(),
               'seconds_since_update': int(time_since_update),
               'is_stale': time_since_update > 300  # 5 minutes
           }

       return JsonResponse({
           'status': 'healthy' if price_feed_status['running'] else 'degraded',
           'timestamp': timezone.now().isoformat(),
           'services': {
               'price_feed': price_feed_status,
               'websocket_connections': connection_stats,
               'data_freshness': data_freshness
           }
       })

Logging Configuration
~~~~~~~~~~~~~~~~~~~~

Configure detailed logging for real-time services:

.. code-block:: python

   # config/settings/production.py
   LOGGING = {
       'version': 1,
       'disable_existing_loggers': False,
       'formatters': {
           'verbose': {
               'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
               'style': '{',
           },
           'json': {
               '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
               'format': '%(levelname)s %(asctime)s %(name)s %(message)s'
           },
       },
       'handlers': {
           'realtime_file': {
               'level': 'INFO',
               'class': 'logging.handlers.RotatingFileHandler',
               'filename': '/var/log/personal-finance/realtime.log',
               'maxBytes': 10485760,  # 10MB
               'backupCount': 5,
               'formatter': 'json',
           },
           'websocket_file': {
               'level': 'INFO',
               'class': 'logging.handlers.RotatingFileHandler',
               'filename': '/var/log/personal-finance/websocket.log',
               'maxBytes': 10485760,
               'backupCount': 3,
               'formatter': 'json',
           },
           'price_feed_file': {
               'level': 'INFO',
               'class': 'logging.handlers.RotatingFileHandler',
               'filename': '/var/log/personal-finance/price_feed.log',
               'maxBytes': 10485760,
               'backupCount': 3,
               'formatter': 'json',
           }
       },
       'loggers': {
           'personal_finance.realtime': {
               'handlers': ['realtime_file'],
               'level': 'INFO',
               'propagate': False,
           },
           'personal_finance.realtime.consumers': {
               'handlers': ['websocket_file'],
               'level': 'INFO',
               'propagate': False,
           },
           'personal_finance.realtime.services': {
               'handlers': ['price_feed_file'],
               'level': 'INFO',
               'propagate': False,
           }
       }
   }

Performance Monitoring
~~~~~~~~~~~~~~~~~~~~~~

Implement performance monitoring and metrics:

.. code-block:: python

   # realtime/monitoring.py
   import time
   import logging
   from django.core.cache import cache
   from django.utils import timezone

   class PerformanceMonitor:
       \"\"\"Monitor real-time service performance.\"\"\"

       def __init__(self):
           self.logger = logging.getLogger('personal_finance.realtime.performance')

       def record_price_update_latency(self, symbol, latency_ms):
           \"\"\"Record price update latency for monitoring.\"\"\"
           cache_key = f'price_update_latency:{symbol}'
           latencies = cache.get(cache_key, [])
           latencies.append(latency_ms)

           # Keep only last 100 measurements
           if len(latencies) > 100:
               latencies = latencies[-100:]

           cache.set(cache_key, latencies, 3600)  # 1 hour

           # Log if latency is high
           if latency_ms > 1000:  # > 1 second
               self.logger.warning(f'High price update latency: {symbol} took {latency_ms}ms')

       def record_websocket_message_latency(self, message_type, latency_ms):
           \"\"\"Record WebSocket message processing latency.\"\"\"
           cache_key = f'websocket_latency:{message_type}'
           latencies = cache.get(cache_key, [])
           latencies.append(latency_ms)

           if len(latencies) > 1000:
               latencies = latencies[-1000:]

           cache.set(cache_key, latencies, 3600)

       def get_performance_metrics(self):
           \"\"\"Get current performance metrics.\"\"\"
           metrics = {}

           # Price update metrics
           price_symbols = ['AAPL', 'GOOGL', 'MSFT']  # Sample symbols
           for symbol in price_symbols:
               cache_key = f'price_update_latency:{symbol}'
               latencies = cache.get(cache_key, [])

               if latencies:
                   metrics[f'price_update_avg_latency_{symbol}'] = sum(latencies) / len(latencies)
                   metrics[f'price_update_max_latency_{symbol}'] = max(latencies)

           # WebSocket metrics
           message_types = ['asset_update', 'portfolio_update']
           for msg_type in message_types:
               cache_key = f'websocket_latency:{msg_type}'
               latencies = cache.get(cache_key, [])

               if latencies:
                   metrics[f'websocket_avg_latency_{msg_type}'] = sum(latencies) / len(latencies)

           return metrics

Troubleshooting
---------------

Common Issues and Solutions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**WebSocket Connection Failures**

.. code-block:: python

   # Debug WebSocket connection issues
   def debug_websocket_connection(request):
       \"\"\"Debug helper for WebSocket connection issues.\"\"\"

       checks = {
           'user_authenticated': request.user.is_authenticated,
           'websocket_endpoint_accessible': True,  # Test this programmatically
           'redis_connection': check_redis_connection(),
           'price_feed_running': PriceFeedService().get_service_status()['running']
       }

       return JsonResponse({
           'debug_info': checks,
           'recommendations': generate_connection_recommendations(checks)
       })

   def check_redis_connection():
       \"\"\"Check Redis connection for WebSocket channels.\"\"\"
       try:
           from django.core.cache import cache
           cache.set('test_key', 'test_value', 10)
           return cache.get('test_key') == 'test_value'
       except:
           return False

**No Price Updates**

.. code-block:: bash

   # Debug price update issues

   # Check service status
   python manage.py monitor_websockets --detailed

   # Test specific asset update
   python manage.py update_asset_prices --symbols AAPL --dry-run --verbose

   # Check API connectivity
   curl -H \"Authorization: Bearer $API_KEY\" https://api.finance.yahoo.com/v1/quote/AAPL

**High Memory Usage**

.. code-block:: python

   # Monitor memory usage
   import psutil

   def monitor_memory_usage():
       \"\"\"Monitor real-time service memory usage.\"\"\"
       process = psutil.Process()
       memory_info = process.memory_info()

       print(f\"RSS Memory: {memory_info.rss / 1024 / 1024:.1f} MB\")
       print(f\"VMS Memory: {memory_info.vms / 1024 / 1024:.1f} MB\")

       # Check connection counts
       connection_manager = ConnectionManager()
       print(f\"Active connections: {connection_manager.get_connection_count()}\")

**Performance Issues**

.. code-block:: python

   # Optimize price update performance
   class OptimizedPriceFeedService:
       def __init__(self):
           self.connection_pool = {}  # Reuse HTTP connections
           self.cache_timeout = 30    # Cache results briefly

       def batch_update_with_caching(self, symbols):
           \"\"\"Update prices with intelligent caching.\"\"\"
           cached_symbols = []
           fresh_symbols = []

           for symbol in symbols:
               cache_key = f'price_cache:{symbol}'
               if cache.get(cache_key):
                   cached_symbols.append(symbol)
               else:
                   fresh_symbols.append(symbol)

           # Only fetch uncached symbols
           if fresh_symbols:
               results = self.fetch_prices(fresh_symbols)

               # Cache results
               for symbol, price_data in results.items():
                   cache_key = f'price_cache:{symbol}'
                   cache.set(cache_key, price_data, self.cache_timeout)

           print(f\"Used cache for {len(cached_symbols)} symbols, fetched {len(fresh_symbols)}\")

Best Practices
--------------

For Developers
~~~~~~~~~~~~~~

1. **Handle Connection Failures Gracefully**

   .. code-block:: javascript

      // Implement exponential backoff for reconnection
      class RobustWebSocketClient {
          constructor(options) {
              this.maxRetries = options.maxRetries || 10;
              this.retryDelay = options.retryDelay || 1000;
              this.retryMultiplier = options.retryMultiplier || 2;
          }

          scheduleReconnect() {
              const delay = Math.min(
                  this.retryDelay * Math.pow(this.retryMultiplier, this.reconnectAttempts),
                  30000  // Max 30 second delay
              );

              setTimeout(() => this.connect(), delay);
          }
      }

2. **Optimize Message Handling**

   .. code-block:: python

      # Use async processing for message handling
      import asyncio

      async def handle_price_update(self, message_data):
          \"\"\"Handle price updates asynchronously.\"\"\"
          tasks = []

          for subscriber in self.subscribers:
              task = asyncio.create_task(
                  subscriber.send_message(message_data)
              )
              tasks.append(task)

          await asyncio.gather(*tasks, return_exceptions=True)

3. **Implement Proper Rate Limiting**

   .. code-block:: python

      from django.core.cache import cache

      def rate_limit_websocket_messages(user, message_type):
          \"\"\"Rate limit WebSocket messages per user.\"\"\"
          cache_key = f'websocket_rate_limit:{user.id}:{message_type}'

          current_count = cache.get(cache_key, 0)
          if current_count >= 60:  # 60 messages per minute
              return False

          cache.set(cache_key, current_count + 1, 60)
          return True

For System Administrators
~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Monitor Resource Usage**

   .. code-block:: bash

      # Monitor WebSocket connections and memory usage
      watch -n 5 'ps aux | grep "start_price_feed\\|daphne" | grep -v grep'

      # Monitor Redis memory usage
      redis-cli info memory

2. **Set Up Alerts**

   .. code-block:: python

      # Set up alerts for service degradation
      def check_service_health():
          status = get_realtime_service_status()

          if status['price_feed_down_time'] > 300:  # 5 minutes
              send_alert('Price feed has been down for 5+ minutes')

          if status['connection_count'] > 1000:
              send_alert('High WebSocket connection count detected')

3. **Regular Maintenance**

   .. code-block:: bash

      # Clean up old logs
      find /var/log/personal-finance/ -name \"*.log\" -mtime +7 -delete

      # Restart services weekly
      sudo systemctl restart personal-finance-price-feed

Security Considerations
-----------------------

1. **Authentication and Authorization**

   .. code-block:: python

      # Ensure proper user authentication
      class SecureRealtimeConsumer(AsyncWebsocketConsumer):
          async def connect(self):
              user = self.scope.get('user')

              if not user or not user.is_authenticated:
                  await self.close(code=4401)  # Unauthorized
                  return

              # Check user permissions
              if not user.has_perm('realtime.access_websocket'):
                  await self.close(code=4403)  # Forbidden
                  return

2. **Data Validation**

   .. code-block:: python

      # Validate all incoming messages
      def validate_websocket_message(message):
          \"\"\"Validate WebSocket message structure and content.\"\"\"
          if not isinstance(message, dict):
              raise ValueError(\"Message must be a dictionary\")

          if 'type' not in message:
              raise ValueError(\"Message must have a 'type' field\")

          if message['type'] not in ALLOWED_MESSAGE_TYPES:
              raise ValueError(f\"Invalid message type: {message['type']}\")

          # Validate message-specific data
          if message['type'] == 'subscribe_asset':
              symbol = message.get('data', {}).get('symbol')
              if not symbol or not validate_asset_symbol(symbol):
                  raise ValueError(\"Invalid asset symbol\")

3. **Rate Limiting and DoS Protection**

   .. code-block:: python

      # Implement comprehensive rate limiting
      class RateLimitedWebSocketConsumer(AsyncWebsocketConsumer):
          async def receive(self, text_data):
              # Check rate limits
              if not self.check_rate_limits():
                  await self.close(code=4429)  # Too Many Requests
                  return

              # Check message size
              if len(text_data) > settings.WEBSOCKET_MESSAGE_SIZE_LIMIT:
                  await self.close(code=4413)  # Request Entity Too Large
                  return

              await super().receive(text_data)

See Also
--------

* :doc:`../api/rest_endpoints` - REST API integration for real-time services
* :doc:`../modules/portfolio` - Portfolio integration for real-time tracking
* :doc:`../config/django_settings` - Real-time configuration settings
* :doc:`../deployment/production` - Production deployment for real-time services
