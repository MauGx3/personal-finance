"""
Test Configuration and Utilities for Personal Finance Platform

This module provides test configuration, fixtures, factories, and utility
functions to support the comprehensive test suite.
"""

import pytest
import time
import json
import random
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings
import factory
from factory.django import DjangoModelFactory

User = get_user_model()


# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================

def pytest_configure(config):
    """Configure pytest settings."""
    # Disable migrations for faster tests
    settings.MIGRATION_MODULES = {
        'auth': None,
        'contenttypes': None,
        'sessions': None,
        'messages': None,
        'staticfiles': None,
        'portfolios': None,
        'assets': None,
        'analytics': None,
        'data_sources': None,
        'backtesting': None,
        'tax': None,
        'visualization': None,
        'realtime': None,
        'users': None,
    }
    
    # Use in-memory database for speed
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
    
    # Disable logging during tests
    settings.LOGGING_CONFIG = None
    
    # Use dummy cache for tests
    settings.CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }


# =============================================================================
# PYTEST FIXTURES
# =============================================================================

@pytest.fixture(scope='session')
def django_db_setup():
    """Set up database for session."""
    from django.test.utils import setup_test_environment, teardown_test_environment
    from django.db import connections
    from django.core.management import call_command
    
    setup_test_environment()
    call_command('migrate', '--run-syncdb', verbosity=0, interactive=False)


@pytest.fixture
def api_client():
    """Provide DRF API test client."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_user(db):
    """Create and return authenticated user."""
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    return user


@pytest.fixture
def authenticated_api_client(api_client, authenticated_user):
    """Provide authenticated API client."""
    api_client.force_authenticate(user=authenticated_user)
    return api_client


@pytest.fixture
def admin_user(db):
    """Create and return admin user."""
    return User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
        is_staff=True,
        is_superuser=True
    )


@pytest.fixture
def sample_portfolio_data():
    """Provide sample portfolio data for testing."""
    return {
        'name': 'Test Portfolio',
        'description': 'Portfolio for testing purposes',
        'positions': [
            {
                'symbol': 'AAPL',
                'quantity': 100,
                'cost_basis': Decimal('150.00'),
                'current_price': Decimal('155.00')
            },
            {
                'symbol': 'GOOGL',
                'quantity': 50,
                'cost_basis': Decimal('2500.00'),
                'current_price': Decimal('2550.00')
            },
            {
                'symbol': 'MSFT',
                'quantity': 75,
                'cost_basis': Decimal('300.00'),
                'current_price': Decimal('320.00')
            }
        ]
    }


@pytest.fixture
def sample_market_data():
    """Provide sample market data for testing."""
    return {
        'AAPL': {
            'symbol': 'AAPL',
            'price': 155.25,
            'change': 2.50,
            'change_percent': 1.64,
            'volume': 50000000,
            'market_cap': 3000000000000,
            'pe_ratio': 25.5,
            'dividend_yield': 0.57
        },
        'GOOGL': {
            'symbol': 'GOOGL',
            'price': 2555.75,
            'change': -15.25,
            'change_percent': -0.59,
            'volume': 1200000,
            'market_cap': 1700000000000,
            'pe_ratio': 22.8,
            'dividend_yield': 0.0
        },
        'MSFT': {
            'symbol': 'MSFT',
            'price': 322.80,
            'change': 5.15,
            'change_percent': 1.62,
            'volume': 25000000,
            'market_cap': 2400000000000,
            'pe_ratio': 28.2,
            'dividend_yield': 0.72
        }
    }


@pytest.fixture
def sample_historical_data():
    """Provide sample historical data for testing."""
    base_date = datetime(2023, 1, 1)
    dates = [(base_date + timedelta(days=i)).isoformat() for i in range(252)]  # One year
    
    # Generate realistic price series
    prices = []
    current_price = 100.0
    
    for _ in range(252):
        # Random walk with slight upward trend
        change = random.gauss(0.001, 0.02)  # 0.1% daily trend, 2% volatility
        current_price *= (1 + change)
        prices.append(round(current_price, 2))
    
    volumes = [random.randint(500000, 5000000) for _ in range(252)]
    
    return {
        'symbol': 'AAPL',
        'dates': dates,
        'prices': prices,
        'volumes': volumes
    }


@pytest.fixture
def mock_external_apis():
    """Provide mock responses for external APIs."""
    return {
        'yahoo_finance': {
            'AAPL': {
                'regularMarketPrice': 155.25,
                'regularMarketChange': 2.50,
                'regularMarketChangePercent': 1.64,
                'regularMarketVolume': 50000000,
                'marketCap': 3000000000000
            }
        },
        'alpha_vantage': {
            'Global Quote': {
                '01. symbol': 'AAPL',
                '02. open': '153.00',
                '03. high': '156.50',
                '04. low': '152.75',
                '05. price': '155.25',
                '06. volume': '50000000',
                '07. latest trading day': '2023-12-01',
                '08. previous close': '152.75',
                '09. change': '2.50',
                '10. change percent': '1.64%'
            }
        },
        'stockdx': {
            'symbol': 'AAPL',
            'price': 155.25,
            'change': 2.50,
            'volume': 50000000,
            'timestamp': '2023-12-01T16:00:00Z'
        }
    }


# =============================================================================
# FACTORY CLASSES
# =============================================================================

class UserFactory(DjangoModelFactory):
    """Factory for creating User instances."""
    
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    is_staff = False
    is_superuser = False


class AdminUserFactory(UserFactory):
    """Factory for creating admin User instances."""
    
    is_staff = True
    is_superuser = True


class PortfolioFactory(DjangoModelFactory):
    """Factory for creating Portfolio instances."""
    
    class Meta:
        model = 'portfolios.Portfolio'  # String reference to avoid import issues
    
    name = factory.Faker('company')
    description = factory.Faker('text', max_nb_chars=200)
    user = factory.SubFactory(UserFactory)
    created_at = factory.Faker('date_time_this_year')
    is_active = True


class AssetFactory(DjangoModelFactory):
    """Factory for creating Asset instances."""
    
    class Meta:
        model = 'assets.Asset'
    
    symbol = factory.Sequence(lambda n: f'STOCK{n:03d}')
    name = factory.Faker('company')
    asset_type = factory.Iterator(['stock', 'etf', 'bond', 'crypto'])
    exchange = factory.Iterator(['NYSE', 'NASDAQ', 'AMEX'])
    currency = 'USD'
    sector = factory.Iterator(['Technology', 'Healthcare', 'Finance', 'Energy', 'Consumer'])
    country = 'US'
    is_active = True


class TransactionFactory(DjangoModelFactory):
    """Factory for creating Transaction instances."""
    
    class Meta:
        model = 'portfolios.Transaction'
    
    portfolio = factory.SubFactory(PortfolioFactory)
    asset = factory.SubFactory(AssetFactory)
    transaction_type = factory.Iterator(['BUY', 'SELL', 'DIVIDEND'])
    quantity = factory.Faker('random_int', min=1, max=1000)
    price = factory.LazyFunction(lambda: Decimal(str(random.uniform(10, 500))))
    commission = factory.LazyFunction(lambda: Decimal(str(random.uniform(0, 10))))
    date = factory.Faker('date_this_year')
    notes = factory.Faker('text', max_nb_chars=100)


class PositionFactory(DjangoModelFactory):
    """Factory for creating Position instances."""
    
    class Meta:
        model = 'portfolios.Position'
    
    portfolio = factory.SubFactory(PortfolioFactory)
    asset = factory.SubFactory(AssetFactory)
    quantity = factory.Faker('random_int', min=1, max=1000)
    average_cost = factory.LazyFunction(lambda: Decimal(str(random.uniform(10, 500))))
    current_price = factory.LazyFunction(lambda: Decimal(str(random.uniform(10, 500))))
    last_updated = factory.Faker('date_time_this_month')


# =============================================================================
# TEST DATA GENERATORS
# =============================================================================

class TestDataGenerator:
    """Generate test data for various scenarios."""
    
    @staticmethod
    def generate_price_series(length=100, start_price=100.0, volatility=0.02, trend=0.001):
        """Generate realistic price series."""
        prices = [start_price]
        
        for _ in range(length - 1):
            change = random.gauss(trend, volatility)
            new_price = prices[-1] * (1 + change)
            prices.append(max(new_price, 0.01))  # Ensure positive prices
        
        return prices
    
    @staticmethod
    def generate_portfolio_data(num_positions=10, total_value_range=(10000, 100000)):
        """Generate realistic portfolio data."""
        symbols = [f'STOCK{i:03d}' for i in range(num_positions)]
        total_value = random.uniform(*total_value_range)
        
        positions = []
        remaining_value = total_value
        
        for i, symbol in enumerate(symbols):
            if i == len(symbols) - 1:
                # Last position gets remaining value
                position_value = remaining_value
            else:
                # Random allocation between 5% and 25% of remaining value
                max_allocation = min(0.25, remaining_value / total_value)
                allocation = random.uniform(0.05, max_allocation)
                position_value = total_value * allocation
                remaining_value -= position_value
            
            # Generate position details
            current_price = random.uniform(10, 500)
            quantity = int(position_value / current_price)
            cost_basis = current_price * random.uniform(0.8, 1.2)  # +/- 20% from current
            
            positions.append({
                'symbol': symbol,
                'quantity': quantity,
                'current_price': Decimal(str(round(current_price, 2))),
                'cost_basis': Decimal(str(round(cost_basis, 2))),
                'market_value': Decimal(str(round(quantity * current_price, 2)))
            })
        
        return positions
    
    @staticmethod
    def generate_transaction_history(symbols, start_date, end_date, frequency='weekly'):
        """Generate transaction history for backtesting."""
        transactions = []
        current_date = start_date
        
        frequency_days = {
            'daily': 1,
            'weekly': 7,
            'monthly': 30,
            'quarterly': 90
        }
        
        step = timedelta(days=frequency_days.get(frequency, 7))
        
        while current_date <= end_date:
            # Random chance of transaction
            if random.random() < 0.3:  # 30% chance of transaction
                symbol = random.choice(symbols)
                transaction_type = random.choice(['BUY', 'SELL'])
                quantity = random.randint(10, 100)
                price = Decimal(str(round(random.uniform(50, 300), 2)))
                
                transactions.append({
                    'date': current_date.isoformat(),
                    'symbol': symbol,
                    'type': transaction_type,
                    'quantity': quantity,
                    'price': price,
                    'commission': Decimal(str(round(random.uniform(1, 10), 2)))
                })
            
            current_date += step
        
        return sorted(transactions, key=lambda x: x['date'])
    
    @staticmethod
    def generate_market_scenarios():
        """Generate various market scenarios for testing."""
        scenarios = {
            'bull_market': {
                'trend': 0.008,  # 0.8% daily trend
                'volatility': 0.015,
                'description': 'Strong upward trend with low volatility'
            },
            'bear_market': {
                'trend': -0.005,  # -0.5% daily trend
                'volatility': 0.025,
                'description': 'Downward trend with higher volatility'
            },
            'sideways_market': {
                'trend': 0.0,  # No trend
                'volatility': 0.02,
                'description': 'Range-bound market with normal volatility'
            },
            'high_volatility': {
                'trend': 0.001,
                'volatility': 0.05,  # Very high volatility
                'description': 'High volatility with minimal trend'
            },
            'market_crash': {
                'trend': -0.03,  # -3% daily (extreme)
                'volatility': 0.08,
                'description': 'Market crash scenario'
            }
        }
        
        return scenarios


# =============================================================================
# TEST UTILITIES
# =============================================================================

class TestUtilities:
    """Utility functions for testing."""
    
    @staticmethod
    def assert_decimal_almost_equal(test_case, decimal1, decimal2, places=2):
        """Assert two decimals are almost equal."""
        quantize_to = Decimal(10) ** -places
        test_case.assertEqual(
            decimal1.quantize(quantize_to),
            decimal2.quantize(quantize_to),
            f"Decimals not equal: {decimal1} != {decimal2}"
        )
    
    @staticmethod
    def assert_percentage_within_range(test_case, percentage, min_val, max_val):
        """Assert percentage is within expected range."""
        test_case.assertGreaterEqual(percentage, min_val)
        test_case.assertLessEqual(percentage, max_val)
    
    @staticmethod
    def create_mock_response(data, status_code=200, headers=None):
        """Create mock HTTP response."""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.json.return_value = data
        mock_response.text = json.dumps(data) if isinstance(data, dict) else str(data)
        mock_response.headers = headers or {}
        return mock_response
    
    @staticmethod
    def measure_performance(func, *args, **kwargs):
        """Measure function performance."""
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        
        return {
            'result': result,
            'execution_time': end_time - start_time,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def generate_test_report(test_results):
        """Generate test execution report."""
        report = {
            'summary': {
                'total_tests': len(test_results),
                'passed': sum(1 for r in test_results if r.get('status') == 'passed'),
                'failed': sum(1 for r in test_results if r.get('status') == 'failed'),
                'skipped': sum(1 for r in test_results if r.get('status') == 'skipped'),
            },
            'execution_times': {
                'total': sum(r.get('execution_time', 0) for r in test_results),
                'average': sum(r.get('execution_time', 0) for r in test_results) / len(test_results) if test_results else 0,
                'slowest': max((r.get('execution_time', 0) for r in test_results), default=0)
            },
            'details': test_results
        }
        
        return report


# =============================================================================
# MOCK FACTORIES
# =============================================================================

class MockFactory:
    """Factory for creating mock objects."""
    
    @staticmethod
    def create_mock_user(user_id=1, username='testuser'):
        """Create mock user object."""
        mock_user = Mock()
        mock_user.id = user_id
        mock_user.username = username
        mock_user.email = f'{username}@example.com'
        mock_user.is_authenticated = True
        mock_user.is_active = True
        mock_user.is_staff = False
        return mock_user
    
    @staticmethod
    def create_mock_portfolio(portfolio_id=1, user=None):
        """Create mock portfolio object."""
        mock_portfolio = Mock()
        mock_portfolio.id = portfolio_id
        mock_portfolio.name = f'Test Portfolio {portfolio_id}'
        mock_portfolio.description = 'Mock portfolio for testing'
        mock_portfolio.user = user or MockFactory.create_mock_user()
        mock_portfolio.created_at = datetime.now()
        mock_portfolio.is_active = True
        return mock_portfolio
    
    @staticmethod
    def create_mock_asset(symbol='AAPL'):
        """Create mock asset object."""
        mock_asset = Mock()
        mock_asset.symbol = symbol
        mock_asset.name = f'{symbol} Test Company'
        mock_asset.asset_type = 'stock'
        mock_asset.exchange = 'NASDAQ'
        mock_asset.currency = 'USD'
        mock_asset.sector = 'Technology'
        mock_asset.country = 'US'
        mock_asset.is_active = True
        return mock_asset
    
    @staticmethod
    def create_mock_position(portfolio=None, asset=None):
        """Create mock position object."""
        mock_position = Mock()
        mock_position.portfolio = portfolio or MockFactory.create_mock_portfolio()
        mock_position.asset = asset or MockFactory.create_mock_asset()
        mock_position.quantity = 100
        mock_position.average_cost = Decimal('150.00')
        mock_position.current_price = Decimal('155.00')
        mock_position.market_value = Decimal('15500.00')
        mock_position.unrealized_gain_loss = Decimal('500.00')
        mock_position.last_updated = datetime.now()
        return mock_position
    
    @staticmethod
    def create_mock_api_response(symbol='AAPL', price=150.00):
        """Create mock API response."""
        return {
            'symbol': symbol,
            'price': price,
            'change': 2.50,
            'change_percent': 1.69,
            'volume': 50000000,
            'market_cap': 3000000000000,
            'timestamp': datetime.now().isoformat()
        }


# =============================================================================
# PERFORMANCE TEST HELPERS
# =============================================================================

class PerformanceTestHelper:
    """Helper class for performance testing."""
    
    @staticmethod
    def benchmark_function(func, iterations=100, warmup=10):
        """Benchmark function performance."""
        # Warmup runs
        for _ in range(warmup):
            func()
        
        # Actual benchmark
        execution_times = []
        for _ in range(iterations):
            start_time = time.perf_counter()
            func()
            end_time = time.perf_counter()
            execution_times.append(end_time - start_time)
        
        return {
            'iterations': iterations,
            'total_time': sum(execution_times),
            'average_time': sum(execution_times) / len(execution_times),
            'min_time': min(execution_times),
            'max_time': max(execution_times),
            'median_time': sorted(execution_times)[len(execution_times) // 2]
        }
    
    @staticmethod
    def stress_test(func, duration_seconds=60, max_concurrent=10):
        """Perform stress test on function."""
        import threading
        import queue
        
        results = queue.Queue()
        start_time = time.time()
        threads = []
        
        def worker():
            while time.time() - start_time < duration_seconds:
                try:
                    execution_start = time.perf_counter()
                    func()
                    execution_end = time.perf_counter()
                    results.put({
                        'success': True,
                        'execution_time': execution_end - execution_start
                    })
                except Exception as e:
                    results.put({
                        'success': False,
                        'error': str(e)
                    })
        
        # Start worker threads
        for _ in range(max_concurrent):
            thread = threading.Thread(target=worker)
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Collect results
        all_results = []
        while not results.empty():
            all_results.append(results.get())
        
        successful = [r for r in all_results if r['success']]
        failed = [r for r in all_results if not r['success']]
        
        return {
            'total_operations': len(all_results),
            'successful_operations': len(successful),
            'failed_operations': len(failed),
            'success_rate': len(successful) / len(all_results) if all_results else 0,
            'average_execution_time': sum(r.get('execution_time', 0) for r in successful) / len(successful) if successful else 0,
            'operations_per_second': len(all_results) / duration_seconds
        }


# =============================================================================
# TEST DECORATORS
# =============================================================================

def skip_if_no_external_apis(test_func):
    """Skip test if external APIs are not available."""
    def wrapper(*args, **kwargs):
        # Check if we should skip external API tests
        if getattr(settings, 'SKIP_EXTERNAL_API_TESTS', True):
            pytest.skip("External API tests disabled")
        return test_func(*args, **kwargs)
    return wrapper


def performance_test(max_execution_time=1.0):
    """Decorator to mark performance tests with time limits."""
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = test_func(*args, **kwargs)
            end_time = time.perf_counter()
            
            execution_time = end_time - start_time
            if execution_time > max_execution_time:
                pytest.fail(f"Test exceeded maximum execution time: {execution_time:.3f}s > {max_execution_time}s")
            
            return result
        return wrapper
    return decorator


def require_redis(test_func):
    """Skip test if Redis is not available."""
    def wrapper(*args, **kwargs):
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.ping()
        except:
            pytest.skip("Redis not available")
        return test_func(*args, **kwargs)
    return wrapper


def require_celery(test_func):
    """Skip test if Celery is not available."""
    def wrapper(*args, **kwargs):
        try:
            from celery import Celery
            # Check if Celery broker is available
            app = Celery('test')
            app.config_from_object('django.conf:settings', namespace='CELERY')
        except:
            pytest.skip("Celery not available")
        return test_func(*args, **kwargs)
    return wrapper


if __name__ == '__main__':
    # Example usage of test utilities
    generator = TestDataGenerator()
    
    # Generate sample data
    prices = generator.generate_price_series(100)
    portfolio = generator.generate_portfolio_data(10)
    scenarios = generator.generate_market_scenarios()
    
    print(f"Generated {len(prices)} price points")
    print(f"Generated portfolio with {len(portfolio)} positions")
    print(f"Available market scenarios: {list(scenarios.keys())}")
    
    # Performance benchmark example
    helper = PerformanceTestHelper()
    
    def sample_calculation():
        return sum(random.random() for _ in range(1000))
    
    benchmark = helper.benchmark_function(sample_calculation, iterations=100)
    print(f"Benchmark results: {benchmark}")