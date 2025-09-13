"""
Enhanced test configuration and utilities for the personal finance platform.

Provides test fixtures, utilities, and configuration for comprehensive testing
across all platform components while avoiding CI/CD issues.
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import transaction
from decimal import Decimal
from datetime import date, datetime, timedelta
import factory
from unittest.mock import Mock, patch
import json

from personal_finance.assets.models import Asset, Portfolio, Holding

User = get_user_model()


# Test Fixtures and Factories
class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating test users."""
    
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"testuser{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True


class AssetFactory(factory.django.DjangoModelFactory):
    """Factory for creating test assets."""
    
    class Meta:
        model = Asset
    
    symbol = factory.Sequence(lambda n: f"TEST{n:03d}")
    name = factory.LazyAttribute(lambda obj: f"{obj.symbol} Corporation")
    asset_type = Asset.ASSET_STOCK
    currency = "USD"
    exchange = "NYSE"
    is_active = True


class PortfolioFactory(factory.django.DjangoModelFactory):
    """Factory for creating test portfolios."""
    
    class Meta:
        model = Portfolio
    
    user = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f"Test Portfolio {n}")
    description = factory.Faker('text', max_nb_chars=200)
    is_default = False


class HoldingFactory(factory.django.DjangoModelFactory):
    """Factory for creating test holdings."""
    
    class Meta:
        model = Holding
    
    user = factory.SubFactory(UserFactory)
    asset = factory.SubFactory(AssetFactory)
    portfolio = factory.SubFactory(PortfolioFactory)
    quantity = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)
    average_price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    currency = "USD"


# Test Utilities
class FinancialTestUtils:
    """Utility functions for financial calculations in tests."""
    
    @staticmethod
    def create_sample_portfolio(user, num_holdings=5):
        """Create a sample portfolio with multiple holdings."""
        portfolio = PortfolioFactory(user=user)
        holdings = []
        
        for i in range(num_holdings):
            asset = AssetFactory()
            holding = HoldingFactory(
                user=user,
                asset=asset,
                portfolio=portfolio,
                quantity=Decimal('100'),
                average_price=Decimal(f'{50 + i * 10}')  # Varied prices
            )
            holdings.append(holding)
        
        return portfolio, holdings
    
    @staticmethod
    def calculate_portfolio_value(holdings):
        """Calculate total portfolio value from holdings."""
        return sum(
            holding.quantity * holding.average_price 
            for holding in holdings
        )
    
    @staticmethod
    def generate_price_series(start_price, num_days, volatility=0.02):
        """Generate realistic price series for testing."""
        import random
        
        prices = [start_price]
        current_price = start_price
        
        for _ in range(num_days - 1):
            # Random walk with drift
            daily_return = random.normalvariate(0, volatility)
            current_price = current_price * (1 + daily_return)
            prices.append(round(current_price, 2))
        
        return [Decimal(str(price)) for price in prices]
    
    @staticmethod
    def create_tax_scenario(user, gain_amount=None, loss_amount=None):
        """Create a tax testing scenario with gains and losses."""
        portfolio = PortfolioFactory(user=user)
        
        scenarios = []
        
        if gain_amount:
            # Create profitable holding
            gain_asset = AssetFactory(symbol="GAIN_ASSET")
            gain_holding = HoldingFactory(
                user=user,
                asset=gain_asset,
                portfolio=portfolio,
                quantity=Decimal('100'),
                average_price=Decimal('50.00')  # Would sell at higher price
            )
            scenarios.append(('gain', gain_holding, gain_amount))
        
        if loss_amount:
            # Create loss holding
            loss_asset = AssetFactory(symbol="LOSS_ASSET")
            loss_holding = HoldingFactory(
                user=user,
                asset=loss_asset,
                portfolio=portfolio,
                quantity=Decimal('100'),
                average_price=Decimal('80.00')  # Would sell at lower price
            )
            scenarios.append(('loss', loss_holding, loss_amount))
        
        return portfolio, scenarios


# Mock Services for Testing
class MockDataService:
    """Mock data service for testing without external API calls."""
    
    def __init__(self):
        self.mock_prices = {}
        self.call_count = 0
    
    def set_mock_price(self, symbol, price):
        """Set mock price for a symbol."""
        self.mock_prices[symbol] = Decimal(str(price))
    
    def get_current_price(self, symbol):
        """Get mock current price."""
        self.call_count += 1
        return self.mock_prices.get(symbol, Decimal('100.00'))
    
    def get_historical_data(self, symbol, start_date, end_date):
        """Get mock historical data."""
        # Generate simple historical data
        days = (end_date - start_date).days
        base_price = self.mock_prices.get(symbol, Decimal('100.00'))
        
        return [
            {
                'date': start_date + timedelta(days=i),
                'price': base_price + Decimal(str(i * 0.5)),  # Trending up
                'volume': 1000000
            }
            for i in range(days + 1)
        ]


class MockWebSocketService:
    """Mock WebSocket service for testing real-time features."""
    
    def __init__(self):
        self.connections = []
        self.messages_sent = []
    
    def connect(self, user_id):
        """Mock WebSocket connection."""
        self.connections.append(user_id)
        return True
    
    def disconnect(self, user_id):
        """Mock WebSocket disconnection."""
        if user_id in self.connections:
            self.connections.remove(user_id)
    
    def send_price_update(self, symbol, price):
        """Mock sending price update."""
        message = {
            'type': 'price_update',
            'symbol': symbol,
            'price': str(price),
            'timestamp': datetime.now().isoformat()
        }
        self.messages_sent.append(message)


# Test Base Classes
class FinancePlatformTestCase(TestCase):
    """Base test case for financial platform tests."""
    
    def setUp(self):
        """Set up common test data."""
        self.user = UserFactory()
        self.asset = AssetFactory()
        self.portfolio = PortfolioFactory(user=self.user)
        self.mock_data_service = MockDataService()
    
    def create_holding(self, **kwargs):
        """Create a holding with default values."""
        defaults = {
            'user': self.user,
            'asset': self.asset,
            'portfolio': self.portfolio,
            'quantity': Decimal('100'),
            'average_price': Decimal('50.00')
        }
        defaults.update(kwargs)
        return HoldingFactory(**defaults)
    
    def assert_decimal_equal(self, first, second, places=2):
        """Assert decimal equality with precision."""
        self.assertEqual(
            round(first, places),
            round(second, places)
        )


# Performance Testing Utilities
class PerformanceTestMixin:
    """Mixin for performance testing."""
    
    def time_operation(self, operation, *args, **kwargs):
        """Time an operation and return duration."""
        start_time = datetime.now()
        result = operation(*args, **kwargs)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        return result, duration
    
    def assert_performance_threshold(self, operation, max_duration, *args, **kwargs):
        """Assert that operation completes within time threshold."""
        result, duration = self.time_operation(operation, *args, **kwargs)
        assert duration <= max_duration, f"Operation took {duration}s, expected <= {max_duration}s"
        return result


# Database Testing Utilities
class DatabaseTestMixin:
    """Mixin for database-related testing."""
    
    def assert_db_query_count(self, expected_count):
        """Context manager to assert database query count."""
        from django.test.utils import override_settings
        from django.db import connection
        
        return self.assertNumQueries(expected_count)
    
    def get_db_query_count(self):
        """Get current database query count."""
        from django.db import connection
        return len(connection.queries)


# API Testing Utilities
class APITestMixin:
    """Mixin for API testing."""
    
    def api_get(self, url, user=None, **kwargs):
        """Make authenticated GET request."""
        if user:
            self.client.force_login(user)
        return self.client.get(url, **kwargs)
    
    def api_post(self, url, data, user=None, **kwargs):
        """Make authenticated POST request."""
        if user:
            self.client.force_login(user)
        return self.client.post(
            url,
            data=json.dumps(data) if isinstance(data, dict) else data,
            content_type='application/json',
            **kwargs
        )
    
    def assert_api_response(self, response, expected_status=200, expected_keys=None):
        """Assert API response format and content."""
        self.assertEqual(response.status_code, expected_status)
        
        if expected_status == 200 and expected_keys:
            data = response.json()
            for key in expected_keys:
                self.assertIn(key, data)


# Security Testing Utilities
class SecurityTestMixin:
    """Mixin for security testing."""
    
    def assert_user_isolation(self, user1, user2, model_class, filter_field='user'):
        """Assert that users can only access their own data."""
        # Create objects for each user
        obj1 = model_class.objects.create(**{filter_field: user1, 'name': 'User 1 Object'})
        obj2 = model_class.objects.create(**{filter_field: user2, 'name': 'User 2 Object'})
        
        # Test isolation
        user1_objects = model_class.objects.filter(**{filter_field: user1})
        user2_objects = model_class.objects.filter(**{filter_field: user2})
        
        self.assertIn(obj1, user1_objects)
        self.assertNotIn(obj2, user1_objects)
        self.assertIn(obj2, user2_objects)
        self.assertNotIn(obj1, user2_objects)
    
    def test_sql_injection_protection(self, url, param_name):
        """Test SQL injection protection for a URL parameter."""
        malicious_values = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; SELECT * FROM assets_asset; --"
        ]
        
        for malicious_value in malicious_values:
            response = self.client.get(url, {param_name: malicious_value})
            # Should not return 500 error or crash
            self.assertNotEqual(response.status_code, 500)


# Data Validation Utilities
class ValidationTestMixin:
    """Mixin for data validation testing."""
    
    def assert_model_validation_error(self, model_class, field_name, invalid_value, **other_fields):
        """Assert that a model field validation fails for invalid value."""
        from django.core.exceptions import ValidationError
        
        obj = model_class(**other_fields, **{field_name: invalid_value})
        
        with self.assertRaises(ValidationError):
            obj.full_clean()
    
    def assert_decimal_precision(self, decimal_value, max_digits, decimal_places):
        """Assert decimal precision constraints."""
        # Check total digits
        total_digits = len(str(decimal_value).replace('.', '').replace('-', ''))
        self.assertLessEqual(total_digits, max_digits)
        
        # Check decimal places
        if '.' in str(decimal_value):
            decimal_digits = len(str(decimal_value).split('.')[1])
            self.assertLessEqual(decimal_digits, decimal_places)


# Test Configuration
@pytest.fixture
def sample_user():
    """Pytest fixture for creating a sample user."""
    return UserFactory()


@pytest.fixture
def sample_portfolio(sample_user):
    """Pytest fixture for creating a sample portfolio."""
    return PortfolioFactory(user=sample_user)


@pytest.fixture
def sample_assets():
    """Pytest fixture for creating sample assets."""
    return [AssetFactory() for _ in range(3)]


@pytest.fixture
def mock_data_service():
    """Pytest fixture for mock data service."""
    service = MockDataService()
    service.set_mock_price('AAPL', '150.00')
    service.set_mock_price('GOOGL', '2500.00')
    service.set_mock_price('MSFT', '300.00')
    return service


@pytest.fixture
def mock_websocket_service():
    """Pytest fixture for mock WebSocket service."""
    return MockWebSocketService()


# Test Categories
class TestCategories:
    """Test categories for organizing test runs."""
    
    UNIT = "unit"
    INTEGRATION = "integration"
    API = "api"
    PERFORMANCE = "performance"
    SECURITY = "security"
    TAX = "tax"
    FINANCIAL = "financial"
    REAL_TIME = "realtime"
    BACKTESTING = "backtesting"


# Test Markers
pytestmark = [
    pytest.mark.django_db,
    pytest.mark.filterwarnings("ignore::DeprecationWarning"),
    pytest.mark.filterwarnings("ignore::PendingDeprecationWarning"),
]


# Custom Assertions
def assert_financial_precision(value, expected, tolerance=Decimal('0.01')):
    """Assert financial value within tolerance."""
    assert abs(value - expected) <= tolerance, f"Expected {expected}, got {value}, tolerance {tolerance}"


def assert_percentage_close(actual, expected, tolerance=0.01):
    """Assert percentage values are close."""
    assert abs(float(actual) - float(expected)) <= tolerance, f"Expected {expected}%, got {actual}%"


def assert_portfolio_balance(holdings):
    """Assert portfolio holdings have valid balances."""
    for holding in holdings:
        assert holding.quantity >= Decimal('0'), f"Negative quantity: {holding.quantity}"
        assert holding.average_price >= Decimal('0'), f"Negative price: {holding.average_price}"


# Test Data Generators
def generate_test_transactions(num_transactions=10):
    """Generate test transaction data."""
    import random
    from datetime import datetime, timedelta
    
    transactions = []
    base_date = datetime.now() - timedelta(days=365)
    
    for i in range(num_transactions):
        transaction = {
            'date': base_date + timedelta(days=random.randint(0, 365)),
            'symbol': random.choice(['AAPL', 'GOOGL', 'MSFT', 'AMZN']),
            'quantity': Decimal(str(random.randint(1, 200))),
            'price': Decimal(str(random.uniform(50, 300))).quantize(Decimal('0.01')),
            'type': random.choice(['BUY', 'SELL'])
        }
        transactions.append(transaction)
    
    return sorted(transactions, key=lambda x: x['date'])


def generate_test_price_data(symbol, days=30):
    """Generate test price data for backtesting."""
    import random
    
    base_price = 100.0
    prices = []
    
    for i in range(days):
        # Simple random walk
        change = random.normalvariate(0, 0.02)  # 2% daily volatility
        base_price *= (1 + change)
        
        prices.append({
            'date': date.today() - timedelta(days=days-i-1),
            'open': round(base_price * 0.995, 2),
            'high': round(base_price * 1.005, 2),
            'low': round(base_price * 0.995, 2),
            'close': round(base_price, 2),
            'volume': random.randint(1000000, 10000000)
        })
    
    return prices


# Test Environment Setup
def setup_test_environment():
    """Set up test environment with sample data."""
    # Clear existing data
    User.objects.all().delete()
    Asset.objects.all().delete()
    Portfolio.objects.all().delete()
    Holding.objects.all().delete()
    
    # Create test users
    users = [UserFactory() for _ in range(3)]
    
    # Create test assets
    assets = [
        AssetFactory(symbol='AAPL', name='Apple Inc.', asset_type=Asset.ASSET_STOCK),
        AssetFactory(symbol='GOOGL', name='Alphabet Inc.', asset_type=Asset.ASSET_STOCK),
        AssetFactory(symbol='SPY', name='SPDR S&P 500 ETF', asset_type=Asset.ASSET_ETF),
        AssetFactory(symbol='BND', name='Vanguard Total Bond Market ETF', asset_type=Asset.ASSET_BOND),
    ]
    
    # Create test portfolios and holdings
    for user in users:
        portfolio = PortfolioFactory(user=user)
        
        for asset in assets[:2]:  # Limit holdings per user
            HoldingFactory(
                user=user,
                asset=asset,
                portfolio=portfolio
            )
    
    return {
        'users': users,
        'assets': assets,
        'portfolios': Portfolio.objects.all(),
        'holdings': Holding.objects.all()
    }


# Test Result Validation
def validate_test_results(test_results):
    """Validate test results and generate report."""
    passed = sum(1 for result in test_results if result['status'] == 'passed')
    failed = sum(1 for result in test_results if result['status'] == 'failed')
    skipped = sum(1 for result in test_results if result['status'] == 'skipped')
    
    total = len(test_results)
    pass_rate = (passed / total) * 100 if total > 0 else 0
    
    return {
        'total_tests': total,
        'passed': passed,
        'failed': failed,
        'skipped': skipped,
        'pass_rate': pass_rate,
        'summary': f"{passed}/{total} tests passed ({pass_rate:.1f}%)"
    }