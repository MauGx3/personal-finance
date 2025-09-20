import sys
from pathlib import Path
import pytest
import os
import django
from django.conf import settings


# Ensure the project's src/ directory is on sys.path so tests and
# VS Code test discovery can import the `personal_finance` package
# without installing the package.
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Add the Django project root to the path
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def pytest_configure():
    """Configure pytest to work with Django."""
    # Set Django settings module
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
    
    # Configure Django
    if not settings.configured:
        django.setup()


@pytest.fixture(scope="session")
def django_db_setup():
    """Set up the test database."""
    # Use the default database setup
    pass


@pytest.fixture
def asset_factory():
    """Factory for creating test assets."""
    def _create_asset(**kwargs):
        from personal_finance.assets.models import Asset
        defaults = {
            'symbol': 'TEST',
            'name': 'Test Asset',
            'asset_type': Asset.ASSET_STOCK,
        }
        defaults.update(kwargs)
        return Asset.objects.create(**defaults)
    return _create_asset


@pytest.fixture
def user_factory():
    """Factory for creating test users."""
    def _create_user(**kwargs):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        defaults = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)
    return _create_user


@pytest.fixture
def portfolio_factory(user_factory):
    """Factory for creating test portfolios."""
    def _create_portfolio(user=None, **kwargs):
        from personal_finance.assets.models import Portfolio
        if user is None:
            user = user_factory()
        defaults = {
            'name': 'Test Portfolio',
            'user': user,
        }
        defaults.update(kwargs)
        return Portfolio.objects.create(**defaults)
    return _create_portfolio


@pytest.fixture
def holding_factory(portfolio_factory, asset_factory):
    """Factory for creating test holdings."""
    def _create_holding(portfolio=None, asset=None, **kwargs):
        from personal_finance.assets.models import Holding
        from decimal import Decimal
        
        if portfolio is None:
            portfolio = portfolio_factory()
        if asset is None:
            asset = asset_factory()
            
        defaults = {
            'portfolio': portfolio,
            'asset': asset,
            'quantity': Decimal('100.00'),
            'cost_basis_per_unit': Decimal('50.00'),
        }
        defaults.update(kwargs)
        return Holding.objects.create(**defaults)
    return _create_holding
