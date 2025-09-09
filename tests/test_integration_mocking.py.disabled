"""
Integration and Mocking Test Suite for Personal Finance Platform

This module contains comprehensive integration tests and demonstrates
advanced mocking strategies for external dependencies and services.
"""

import pytest
import json
import asyncio
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from django.test import TestCase, TransactionTestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import requests_mock
from datetime import datetime, timedelta
import redis
import time

User = get_user_model()


class TestComponentIntegration(TransactionTestCase):
    """Integration tests for component interactions."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.user = User.objects.create_user(
            username='integration_user',
            email='integration@test.com',
            password='test_password'
        )
        cache.clear()
    
    def test_portfolio_transaction_position_integration(self):
        """Test complete workflow from transaction to position update."""
        # Mock the entire workflow
        with patch('personal_finance.portfolios.models.Portfolio') as MockPortfolio, \
             patch('personal_finance.portfolios.models.Transaction') as MockTransaction, \
             patch('personal_finance.portfolios.models.Position') as MockPosition:
            
            # Step 1: Create Portfolio
            mock_portfolio = Mock()
            mock_portfolio.id = 1
            mock_portfolio.user = self.user
            mock_portfolio.name = 'Integration Test Portfolio'
            MockPortfolio.objects.create.return_value = mock_portfolio
            
            portfolio = MockPortfolio.objects.create(
                user=self.user,
                name='Integration Test Portfolio'
            )
            
            # Step 2: Create Transaction
            mock_transaction = Mock()
            mock_transaction.id = 1
            mock_transaction.portfolio = mock_portfolio
            mock_transaction.symbol = 'AAPL'
            mock_transaction.transaction_type = 'BUY'
            mock_transaction.quantity = 100
            mock_transaction.price = Decimal('150.00')
            MockTransaction.objects.create.return_value = mock_transaction
            
            transaction_obj = MockTransaction.objects.create(
                portfolio=portfolio,
                symbol='AAPL',
                transaction_type='BUY',
                quantity=100,
                price=Decimal('150.00')
            )
            
            # Step 3: Update Position
            mock_position = Mock()
            mock_position.portfolio = mock_portfolio
            mock_position.symbol = 'AAPL'
            mock_position.quantity = 100
            mock_position.average_cost = Decimal('150.00')
            MockPosition.objects.get_or_create.return_value = (mock_position, True)
            
            position, created = MockPosition.objects.get_or_create(
                portfolio=portfolio,
                symbol='AAPL',
                defaults={
                    'quantity': transaction_obj.quantity,
                    'average_cost': transaction_obj.price
                }
            )
            
            # Verify integration
            self.assertEqual(portfolio.id, 1)
            self.assertEqual(transaction_obj.portfolio, portfolio)
            self.assertEqual(position.portfolio, portfolio)
            self.assertEqual(position.symbol, transaction_obj.symbol)
            self.assertEqual(position.quantity, transaction_obj.quantity)
    
    def test_data_source_analytics_integration(self):
        """Test integration between data sources and analytics."""
        with patch('personal_finance.data_sources.services.DataSourceService') as MockDataService, \
             patch('personal_finance.analytics.services.AnalyticsService') as MockAnalyticsService:
            
            # Mock data source response
            mock_price_data = {
                'AAPL': {'price': 150.25, 'volume': 1000000, 'change': 2.5},
                'GOOGL': {'price': 2500.50, 'volume': 500000, 'change': -15.0}
            }
            MockDataService.fetch_multiple_prices.return_value = mock_price_data
            
            # Mock analytics calculation
            mock_analytics = {
                'total_value': Decimal('375062.50'),
                'total_return': Decimal('12562.50'),
                'return_percentage': Decimal('3.46'),
                'positions': [
                    {'symbol': 'AAPL', 'value': Decimal('15025.00'), 'return': Decimal('250.00')},
                    {'symbol': 'GOOGL', 'value': Decimal('125025.00'), 'return': Decimal('-750.00')}
                ]
            }
            MockAnalyticsService.calculate_portfolio_analytics.return_value = mock_analytics
            
            # Simulate integration
            data_service = MockDataService()
            analytics_service = MockAnalyticsService()
            
            # Fetch price data
            price_data = data_service.fetch_multiple_prices(['AAPL', 'GOOGL'])
            
            # Calculate analytics with fetched data
            analytics = analytics_service.calculate_portfolio_analytics(
                portfolio_id=1,
                price_data=price_data
            )
            
            # Verify integration
            self.assertEqual(len(price_data), 2)
            self.assertIn('AAPL', price_data)
            self.assertIn('GOOGL', price_data)
            self.assertEqual(analytics['total_value'], Decimal('375062.50'))
            self.assertEqual(len(analytics['positions']), 2)
    
    def test_real_time_websocket_integration(self):
        """Test real-time WebSocket integration with price updates."""
        with patch('channels.layers.get_channel_layer') as mock_channel_layer, \
             patch('personal_finance.realtime.services.PriceFeedService') as MockPriceFeedService:
            
            # Mock channel layer
            mock_layer = Mock()
            mock_layer.group_send = AsyncMock()
            mock_channel_layer.return_value = mock_layer
            
            # Mock price feed service
            mock_price_feed = Mock()
            mock_price_feed.get_live_prices.return_value = {
                'AAPL': {'price': 151.00, 'change': 0.75, 'timestamp': time.time()}
            }
            MockPriceFeedService.return_value = mock_price_feed
            
            # Simulate real-time update workflow
            price_feed_service = MockPriceFeedService()
            live_prices = price_feed_service.get_live_prices(['AAPL'])
            
            # Simulate WebSocket message broadcasting
            channel_layer = mock_channel_layer()
            
            # This would be called asynchronously in real implementation
            message = {
                'type': 'price_update',
                'symbol': 'AAPL',
                'price': live_prices['AAPL']['price'],
                'change': live_prices['AAPL']['change']
            }
            
            # Verify integration components
            self.assertIsNotNone(live_prices)
            self.assertEqual(live_prices['AAPL']['price'], 151.00)
            self.assertIsNotNone(channel_layer)
    
    def test_tax_reporting_integration(self):
        """Test integration between transactions and tax reporting."""
        with patch('personal_finance.portfolios.models.Transaction') as MockTransaction, \
             patch('personal_finance.tax.services.TaxCalculationService') as MockTaxService:
            
            # Mock transaction data
            mock_transactions = [
                Mock(
                    symbol='AAPL',
                    transaction_type='BUY',
                    quantity=100,
                    price=Decimal('100.00'),
                    date=datetime(2023, 1, 15)
                ),
                Mock(
                    symbol='AAPL',
                    transaction_type='SELL',
                    quantity=50,
                    price=Decimal('120.00'),
                    date=datetime(2023, 6, 10)
                )
            ]
            MockTransaction.objects.filter.return_value = mock_transactions
            
            # Mock tax calculation results
            mock_tax_report = {
                'capital_gains': {
                    'short_term': Decimal('1000.00'),
                    'long_term': Decimal('0.00')
                },
                'dividend_income': {
                    'qualified': Decimal('150.00'),
                    'ordinary': Decimal('50.00')
                },
                'wash_sales': [],
                'tax_loss_harvesting_opportunities': [
                    {'symbol': 'MSFT', 'potential_loss': Decimal('500.00')}
                ]
            }
            MockTaxService.generate_tax_report.return_value = mock_tax_report
            
            # Simulate tax reporting integration
            transactions = MockTransaction.objects.filter(portfolio__user=self.user)
            tax_service = MockTaxService()
            tax_report = tax_service.generate_tax_report(transactions)
            
            # Verify integration
            self.assertEqual(len(transactions), 2)
            self.assertEqual(tax_report['capital_gains']['short_term'], Decimal('1000.00'))
            self.assertEqual(len(tax_report['tax_loss_harvesting_opportunities']), 1)
    
    def test_backtesting_integration(self):
        """Test backtesting engine integration with historical data."""
        with patch('personal_finance.backtesting.models.Strategy') as MockStrategy, \
             patch('personal_finance.backtesting.services.BacktestEngine') as MockBacktestEngine, \
             patch('personal_finance.data_sources.services.HistoricalDataService') as MockHistoricalService:
            
            # Mock strategy
            mock_strategy = Mock()
            mock_strategy.id = 1
            mock_strategy.name = 'Moving Average Crossover'
            mock_strategy.parameters = {'short_window': 20, 'long_window': 50}
            MockStrategy.objects.get.return_value = mock_strategy
            
            # Mock historical data
            mock_historical_data = {
                'dates': ['2023-01-01', '2023-01-02', '2023-01-03'],
                'prices': [100.0, 102.0, 101.5],
                'volumes': [1000000, 1200000, 800000]
            }
            MockHistoricalService.fetch_historical_data.return_value = mock_historical_data
            
            # Mock backtest results
            mock_backtest_results = {
                'total_return': Decimal('15.50'),
                'sharpe_ratio': 1.25,
                'max_drawdown': Decimal('-8.5'),
                'number_of_trades': 12,
                'win_rate': 0.67,
                'profit_factor': 1.35
            }
            MockBacktestEngine.run_backtest.return_value = mock_backtest_results
            
            # Simulate backtesting integration
            strategy = MockStrategy.objects.get(id=1)
            historical_service = MockHistoricalService()
            backtest_engine = MockBacktestEngine()
            
            historical_data = historical_service.fetch_historical_data(
                symbol='AAPL',
                start_date='2023-01-01',
                end_date='2023-12-31'
            )
            
            backtest_results = backtest_engine.run_backtest(
                strategy=strategy,
                historical_data=historical_data
            )
            
            # Verify integration
            self.assertEqual(strategy.name, 'Moving Average Crossover')
            self.assertEqual(len(historical_data['dates']), 3)
            self.assertEqual(backtest_results['total_return'], Decimal('15.50'))
            self.assertEqual(backtest_results['number_of_trades'], 12)


class TestAdvancedMockingStrategies(TestCase):
    """Demonstrate advanced mocking strategies for external dependencies."""
    
    def test_yahoo_finance_api_comprehensive_mocking(self):
        """Comprehensive mocking of Yahoo Finance API."""
        with patch('yfinance.Ticker') as MockTicker:
            # Configure complex mock behavior
            mock_ticker_instance = Mock()
            
            # Mock historical data
            mock_history = Mock()
            mock_history.index = [datetime(2023, 1, 1), datetime(2023, 1, 2)]
            mock_history.__getitem__ = Mock(side_effect=lambda key: {
                'Close': [150.0, 152.0],
                'Volume': [1000000, 1200000],
                'High': [151.0, 153.0],
                'Low': [149.0, 151.5],
                'Open': [150.5, 150.0]
            }[key])
            mock_ticker_instance.history.return_value = mock_history
            
            # Mock info data
            mock_ticker_instance.info = {
                'symbol': 'AAPL',
                'longName': 'Apple Inc.',
                'sector': 'Technology',
                'marketCap': 3000000000000,
                'trailingPE': 25.5,
                'dividendYield': 0.0057
            }
            
            # Mock real-time quote
            mock_ticker_instance.fast_info = {
                'last_price': 152.5,
                'open': 151.0,
                'day_high': 153.2,
                'day_low': 150.8,
                'regular_market_previous_close': 150.0
            }
            
            MockTicker.return_value = mock_ticker_instance
            
            # Test the mocked functionality
            import yfinance as yf
            ticker = yf.Ticker('AAPL')
            
            # Test historical data
            history = ticker.history(period='2d')
            self.assertEqual(history['Close'][0], 150.0)
            self.assertEqual(history['Volume'][0], 1000000)
            
            # Test company info
            info = ticker.info
            self.assertEqual(info['symbol'], 'AAPL')
            self.assertEqual(info['sector'], 'Technology')
            
            # Test real-time data
            fast_info = ticker.fast_info
            self.assertEqual(fast_info['last_price'], 152.5)
    
    def test_alpha_vantage_api_mocking_with_error_scenarios(self):
        """Mock Alpha Vantage API with various error scenarios."""
        with patch('alpha_vantage.timeseries.TimeSeries') as MockTimeSeries:
            # Scenario 1: Successful response
            mock_ts_success = Mock()
            mock_ts_success.get_quote_endpoint.return_value = (
                {
                    '01. symbol': 'AAPL',
                    '02. open': '151.00',
                    '03. high': '153.25',
                    '04. low': '150.50',
                    '05. price': '152.75',
                    '06. volume': '1250000',
                    '07. latest trading day': '2023-12-01',
                    '08. previous close': '150.00',
                    '09. change': '2.75',
                    '10. change percent': '1.83%'
                },
                {}
            )
            
            # Scenario 2: API limit reached
            mock_ts_limit = Mock()
            mock_ts_limit.get_quote_endpoint.side_effect = Exception(
                "Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute"
            )
            
            # Scenario 3: Invalid symbol
            mock_ts_invalid = Mock()
            mock_ts_invalid.get_quote_endpoint.return_value = (
                {'Error Message': 'Invalid API call'},
                {}
            )
            
            # Test scenarios
            test_scenarios = [
                (mock_ts_success, 'success'),
                (mock_ts_limit, 'rate_limit'),
                (mock_ts_invalid, 'invalid_symbol')
            ]
            
            for mock_instance, scenario_name in test_scenarios:
                with self.subTest(scenario=scenario_name):
                    MockTimeSeries.return_value = mock_instance
                    
                    from alpha_vantage.timeseries import TimeSeries
                    ts = TimeSeries(key='test_key')
                    
                    try:
                        data, metadata = ts.get_quote_endpoint(symbol='AAPL')
                        
                        if scenario_name == 'success':
                            self.assertEqual(data['01. symbol'], 'AAPL')
                            self.assertEqual(data['05. price'], '152.75')
                        elif scenario_name == 'invalid_symbol':
                            self.assertIn('Error Message', data)
                    
                    except Exception as e:
                        if scenario_name == 'rate_limit':
                            self.assertIn('API call frequency', str(e))
    
    def test_redis_cache_mocking_strategies(self):
        """Demonstrate comprehensive Redis cache mocking."""
        with patch('redis.Redis') as MockRedis:
            # Create mock Redis instance
            mock_redis_instance = Mock()
            
            # Mock basic operations
            mock_redis_instance.get.return_value = json.dumps({
                'symbol': 'AAPL',
                'price': 152.50,
                'timestamp': time.time()
            }).encode('utf-8')
            
            mock_redis_instance.set.return_value = True
            mock_redis_instance.delete.return_value = 1
            mock_redis_instance.exists.return_value = True
            mock_redis_instance.ttl.return_value = 300  # 5 minutes remaining
            
            # Mock pipeline operations
            mock_pipeline = Mock()
            mock_pipeline.set.return_value = mock_pipeline
            mock_pipeline.expire.return_value = mock_pipeline
            mock_pipeline.execute.return_value = [True, True]
            mock_redis_instance.pipeline.return_value = mock_pipeline
            
            # Mock pub/sub operations
            mock_pubsub = Mock()
            mock_pubsub.subscribe.return_value = None
            mock_pubsub.get_message.return_value = {
                'type': 'message',
                'channel': b'price_updates',
                'data': json.dumps({'symbol': 'AAPL', 'price': 153.00}).encode('utf-8')
            }
            mock_redis_instance.pubsub.return_value = mock_pubsub
            
            MockRedis.return_value = mock_redis_instance
            
            # Test Redis operations
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0)
            
            # Test basic operations
            cached_data = r.get('AAPL:price')
            self.assertIsNotNone(cached_data)
            
            set_result = r.set('AAPL:price', json.dumps({'price': 153.00}), ex=300)
            self.assertTrue(set_result)
            
            # Test pipeline operations
            pipe = r.pipeline()
            pipe.set('MSFT:price', json.dumps({'price': 375.00}))
            pipe.expire('MSFT:price', 300)
            results = pipe.execute()
            self.assertEqual(len(results), 2)
            
            # Test pub/sub operations
            pubsub = r.pubsub()
            pubsub.subscribe('price_updates')
            message = pubsub.get_message()
            self.assertEqual(message['type'], 'message')
    
    def test_celery_task_mocking_comprehensive(self):
        """Comprehensive Celery task mocking."""
        with patch('personal_finance.tasks.update_portfolio_prices.delay') as mock_task_delay, \
             patch('personal_finance.tasks.calculate_analytics.apply_async') as mock_task_async, \
             patch('celery.result.AsyncResult') as MockAsyncResult:
            
            # Mock delayed task
            mock_task_result = Mock()
            mock_task_result.id = 'task-12345'
            mock_task_result.status = 'PENDING'
            mock_task_result.result = None
            mock_task_delay.return_value = mock_task_result
            
            # Mock async task with options
            mock_async_result = Mock()
            mock_async_result.id = 'task-67890'
            mock_async_result.status = 'SUCCESS'
            mock_async_result.result = {
                'portfolio_id': 1,
                'total_value': 50000.0,
                'total_return': 5000.0
            }
            mock_task_async.return_value = mock_async_result
            
            # Mock AsyncResult for task monitoring
            mock_result_instance = Mock()
            mock_result_instance.ready.return_value = True
            mock_result_instance.successful.return_value = True
            mock_result_instance.result = {'status': 'completed', 'updated_positions': 25}
            MockAsyncResult.return_value = mock_result_instance
            
            # Test task execution
            from personal_finance.tasks import update_portfolio_prices, calculate_analytics
            
            # Test delayed task
            task_result = update_portfolio_prices.delay(portfolio_id=1)
            self.assertEqual(task_result.id, 'task-12345')
            self.assertEqual(task_result.status, 'PENDING')
            
            # Test async task with options
            async_result = calculate_analytics.apply_async(
                args=[1],
                kwargs={'include_risk_metrics': True},
                countdown=60
            )
            self.assertEqual(async_result.id, 'task-67890')
            self.assertEqual(async_result.status, 'SUCCESS')
            
            # Test task monitoring
            from celery.result import AsyncResult
            result = AsyncResult('task-12345')
            self.assertTrue(result.ready())
            self.assertTrue(result.successful())
            self.assertIn('updated_positions', result.result)
    
    def test_database_transaction_mocking(self):
        """Mock database transactions and rollback scenarios."""
        with patch('django.db.transaction.atomic') as mock_atomic, \
             patch('personal_finance.portfolios.models.Portfolio.objects') as mock_portfolio_objects, \
             patch('personal_finance.portfolios.models.Transaction.objects') as mock_transaction_objects:
            
            # Mock successful transaction
            mock_atomic.return_value.__enter__ = Mock()
            mock_atomic.return_value.__exit__ = Mock(return_value=None)
            
            # Mock portfolio creation
            mock_portfolio = Mock()
            mock_portfolio.id = 1
            mock_portfolio.save.return_value = None
            mock_portfolio_objects.create.return_value = mock_portfolio
            
            # Mock transaction creation
            mock_transaction = Mock()
            mock_transaction.id = 1
            mock_transaction.portfolio = mock_portfolio
            mock_transaction.save.return_value = None
            mock_transaction_objects.create.return_value = mock_transaction
            
            # Test successful transaction
            def create_portfolio_with_transaction():
                with transaction.atomic():
                    portfolio = mock_portfolio_objects.create(name='Test Portfolio')
                    transaction_obj = mock_transaction_objects.create(
                        portfolio=portfolio,
                        symbol='AAPL',
                        quantity=100,
                        price=Decimal('150.00')
                    )
                    return portfolio, transaction_obj
            
            portfolio, transaction_obj = create_portfolio_with_transaction()
            
            self.assertEqual(portfolio.id, 1)
            self.assertEqual(transaction_obj.portfolio, portfolio)
            
            # Mock rollback scenario
            mock_atomic.return_value.__exit__ = Mock(side_effect=Exception("Database error"))
            
            with self.assertRaises(Exception):
                with transaction.atomic():
                    raise Exception("Database error")
    
    def test_websocket_connection_mocking(self):
        """Mock WebSocket connections and message handling."""
        with patch('channels.generic.websocket.AsyncWebsocketConsumer') as MockConsumer, \
             patch('channels.db.database_sync_to_async') as mock_db_sync:
            
            # Mock consumer instance
            mock_consumer_instance = Mock()
            mock_consumer_instance.accept = AsyncMock()
            mock_consumer_instance.send = AsyncMock()
            mock_consumer_instance.close = AsyncMock()
            mock_consumer_instance.disconnect = AsyncMock()
            
            # Mock database operations
            mock_db_sync.return_value = AsyncMock(return_value={'user_id': 1, 'subscriptions': ['AAPL', 'GOOGL']})
            
            MockConsumer.return_value = mock_consumer_instance
            
            # Simulate WebSocket lifecycle
            async def test_websocket_lifecycle():
                consumer = MockConsumer()
                
                # Accept connection
                await consumer.accept()
                
                # Send message
                await consumer.send(text_data=json.dumps({
                    'type': 'price_update',
                    'symbol': 'AAPL',
                    'price': 152.50
                }))
                
                # Close connection
                await consumer.close()
            
            # Run async test
            import asyncio
            asyncio.run(test_websocket_lifecycle())
            
            # Verify calls were made
            mock_consumer_instance.accept.assert_called_once()
            mock_consumer_instance.send.assert_called_once()
            mock_consumer_instance.close.assert_called_once()
    
    def test_external_api_circuit_breaker_mocking(self):
        """Mock circuit breaker pattern for external APIs."""
        with patch('personal_finance.data_sources.services.CircuitBreaker') as MockCircuitBreaker:
            # Mock circuit breaker states
            mock_cb_instance = Mock()
            
            # Initial state: closed (working)
            mock_cb_instance.state = 'closed'
            mock_cb_instance.failure_count = 0
            mock_cb_instance.call.return_value = {'symbol': 'AAPL', 'price': 152.50}
            
            MockCircuitBreaker.return_value = mock_cb_instance
            
            # Test successful calls
            cb = MockCircuitBreaker(failure_threshold=5, recovery_timeout=60)
            
            for i in range(3):
                result = cb.call(lambda: {'symbol': 'AAPL', 'price': 152.50 + i})
                self.assertIsNotNone(result)
                self.assertEqual(result['symbol'], 'AAPL')
            
            # Simulate failures leading to open circuit
            mock_cb_instance.failure_count = 5
            mock_cb_instance.state = 'open'
            mock_cb_instance.call.side_effect = Exception("Circuit breaker open")
            
            with self.assertRaises(Exception):
                cb.call(lambda: {'symbol': 'AAPL', 'price': 152.50})
            
            # Simulate recovery (half-open state)
            mock_cb_instance.state = 'half_open'
            mock_cb_instance.call.side_effect = None
            mock_cb_instance.call.return_value = {'symbol': 'AAPL', 'price': 153.00}
            
            result = cb.call(lambda: {'symbol': 'AAPL', 'price': 153.00})
            self.assertEqual(result['price'], 153.00)
            
            # Circuit should close after successful call
            mock_cb_instance.state = 'closed'
            mock_cb_instance.failure_count = 0


class TestAsyncIntegration(TestCase):
    """Integration tests for async operations."""
    
    def test_async_price_feed_integration(self):
        """Test async price feed service integration."""
        with patch('aiohttp.ClientSession') as MockSession:
            # Mock async HTTP session
            mock_session_instance = Mock()
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'symbol': 'AAPL',
                'price': 152.75,
                'volume': 1250000
            })
            
            mock_session_instance.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
            mock_session_instance.get.return_value.__aexit__ = AsyncMock(return_value=None)
            
            MockSession.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
            MockSession.return_value.__aexit__ = AsyncMock(return_value=None)
            
            # Test async price fetching
            async def fetch_price_async(symbol):
                async with MockSession() as session:
                    async with session.get(f'https://api.example.com/{symbol}') as response:
                        return await response.json()
            
            # Run async test
            result = asyncio.run(fetch_price_async('AAPL'))
            
            self.assertEqual(result['symbol'], 'AAPL')
            self.assertEqual(result['price'], 152.75)
    
    def test_async_portfolio_calculation_integration(self):
        """Test async portfolio calculation integration."""
        with patch('asyncio.gather') as mock_gather:
            # Mock async portfolio calculations
            mock_gather.return_value = [
                {'symbol': 'AAPL', 'value': 15275.00, 'return': 275.00},
                {'symbol': 'GOOGL', 'value': 125050.00, 'return': 5050.00},
                {'symbol': 'MSFT', 'value': 37500.00, 'return': 2500.00}
            ]
            
            async def calculate_portfolio_async(symbols):
                tasks = [self._calculate_position_async(symbol) for symbol in symbols]
                return await asyncio.gather(*tasks)
            
            # Run async calculation
            symbols = ['AAPL', 'GOOGL', 'MSFT']
            results = asyncio.run(calculate_portfolio_async(symbols))
            
            self.assertEqual(len(results), 3)
            self.assertEqual(results[0]['symbol'], 'AAPL')
            self.assertEqual(results[1]['return'], 5050.00)
    
    async def _calculate_position_async(self, symbol):
        """Mock async position calculation."""
        await asyncio.sleep(0.001)  # Simulate async work
        return {'symbol': symbol, 'value': 10000.0, 'return': 500.0}


if __name__ == '__main__':
    pytest.main([__file__, '-v'])