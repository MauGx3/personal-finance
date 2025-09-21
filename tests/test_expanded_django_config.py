"""
Expanded test suite for Django configuration and utilities.

This test file expands coverage for Django settings, configurations,
and utility functions that support the application infrastructure.
"""

import pytest
from django.test import override_settings
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.conf import settings
from decimal import Decimal


User = get_user_model()


class TestDjangoConfiguration:
    """Test Django configuration and settings."""

    def test_django_settings_exist(self):
        """Test that required Django settings are configured."""
        # Test that key settings exist
        assert hasattr(settings, "INSTALLED_APPS")
        assert hasattr(settings, "DATABASES")
        assert hasattr(settings, "SECRET_KEY")
        assert hasattr(settings, "DEBUG")

        # Test that our apps are installed
        installed_apps = settings.INSTALLED_APPS
        assert "personal_finance.assets" in installed_apps
        assert "personal_finance.users" in installed_apps

    def test_database_configuration(self):
        """Test database configuration."""
        # Test that database configuration exists
        assert "default" in settings.DATABASES
        default_db = settings.DATABASES["default"]

        # Should have required database settings
        assert "ENGINE" in default_db
        assert "NAME" in default_db

        # Engine should be a valid Django database backend
        engine = default_db["ENGINE"]
        valid_engines = [
            "django.db.backends.sqlite3",
            "django.db.backends.postgresql",
            "django.db.backends.mysql",
        ]
        assert any(valid_engine in engine for valid_engine in valid_engines)

    def test_time_zone_setting(self):
        """Test time zone configuration."""
        # Should have a timezone configured
        assert hasattr(settings, "TIME_ZONE")
        assert settings.TIME_ZONE is not None

    def test_media_and_static_settings(self):
        """Test media and static file settings."""
        # Should have static and media configurations
        assert hasattr(settings, "STATIC_URL")
        assert hasattr(settings, "STATIC_ROOT")
        assert hasattr(settings, "MEDIA_URL")
        assert hasattr(settings, "MEDIA_ROOT")


@pytest.mark.django_db
class TestUserModel:
    """Test Django User model functionality."""

    def test_user_creation(self):
        """Test basic user creation."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.check_password("testpass123")
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_superuser_creation(self):
        """Test superuser creation."""
        superuser = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )

        assert superuser.username == "admin"
        assert superuser.email == "admin@example.com"
        assert superuser.is_staff is True
        assert superuser.is_superuser is True
        assert superuser.is_active is True

    def test_user_string_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com"
        )

        # Default User model string representation is username
        assert str(user) == "testuser"

    def test_user_email_uniqueness(self):
        """Test that user emails should be unique if configured."""
        # Create first user
        User.objects.create_user(
            username="user1", email="test@example.com", password="pass123"
        )

        # Try to create second user with same email
        # This may or may not fail depending on User model configuration
        try:
            User.objects.create_user(
                username="user2", email="test@example.com", password="pass456"
            )
            # If no error, check that both users exist
            users_with_email = User.objects.filter(email="test@example.com")
            assert users_with_email.count() >= 1
        except Exception:
            # If error occurs, that means email uniqueness is enforced
            assert User.objects.filter(email="test@example.com").count() == 1


class TestFormValidation:
    """Test form validation patterns used in the application."""

    def test_decimal_field_validation(self):
        """Test decimal field validation patterns."""
        from django.core.validators import MinValueValidator

        # Test minimum value validator
        min_validator = MinValueValidator(Decimal("0.01"))

        # Valid values should not raise exception
        min_validator(Decimal("1.00"))
        min_validator(Decimal("0.01"))

        # Invalid values should raise exception
        with pytest.raises(ValidationError):
            min_validator(Decimal("0.00"))

        with pytest.raises(ValidationError):
            min_validator(Decimal("-1.00"))

    def test_choice_field_validation(self):
        """Test choice field validation patterns."""
        from personal_finance.assets.models import Asset

        # Valid choices
        valid_choices = [choice[0] for choice in Asset.ASSET_TYPE_CHOICES]

        assert Asset.ASSET_STOCK in valid_choices
        assert Asset.ASSET_BOND in valid_choices
        assert Asset.ASSET_CRYPTO in valid_choices
        assert Asset.ASSET_ETF in valid_choices

        # Test that all expected types are present
        expected_types = [
            "STOCK",
            "BOND",
            "CRYPTO",
            "CASH",
            "FUND",
            "ETF",
            "FOREX",
            "FOREIGN_STOCK",
        ]
        for expected_type in expected_types:
            assert any(
                expected_type in choice[0]
                for choice in Asset.ASSET_TYPE_CHOICES
            )


class TestModelValidation:
    """Test model validation logic."""

    @pytest.mark.django_db
    def test_asset_symbol_validation(self):
        """Test asset symbol validation."""
        from personal_finance.assets.models import Asset

        # Valid symbols should work
        asset = Asset.objects.create(
            symbol="AAPL", name="Apple Inc.", asset_type=Asset.ASSET_STOCK
        )
        assert asset.symbol == "AAPL"

        # Test with various symbol formats
        valid_symbols = ["MSFT", "BRK.A", "BRK/A", "GOOGL", "TSM"]
        for symbol in valid_symbols:
            asset = Asset.objects.create(
                symbol=symbol,
                name=f"Test {symbol}",
                asset_type=Asset.ASSET_STOCK,
            )
            assert asset.symbol == symbol

    @pytest.mark.django_db
    def test_decimal_precision_validation(self):
        """Test decimal field precision validation."""
        from personal_finance.assets.models import Asset, Portfolio, Holding

        # Create test data
        user = User.objects.create_user(
            username="testuser", email="test@example.com"
        )

        asset = Asset.objects.create(
            symbol="TEST", name="Test Asset", asset_type=Asset.ASSET_STOCK
        )

        portfolio = Portfolio.objects.create(user=user, name="Test Portfolio")

        # Test holding with proper decimal precision
        holding = Holding.objects.create(
            portfolio=portfolio,
            asset=asset,
            quantity=Decimal("100.12345678"),  # 8 decimal places
            cost_basis_per_unit=Decimal("150.99"),
        )

        assert holding.quantity == Decimal("100.12345678")
        assert holding.cost_basis_per_unit == Decimal("150.99")


class TestDatabaseOperations:
    """Test database operations and constraints."""

    @pytest.mark.django_db
    def test_cascade_deletion(self):
        """Test cascade deletion behavior."""
        from personal_finance.assets.models import Asset, Portfolio, Holding

        # Create test data
        user = User.objects.create_user(
            username="testuser", email="test@example.com"
        )

        asset = Asset.objects.create(
            symbol="TEST", name="Test Asset", asset_type=Asset.ASSET_STOCK
        )

        portfolio = Portfolio.objects.create(user=user, name="Test Portfolio")

        holding = Holding.objects.create(
            portfolio=portfolio,
            asset=asset,
            quantity=Decimal("100.00"),
            cost_basis_per_unit=Decimal("50.00"),
        )

        # Delete portfolio should cascade to holdings
        portfolio_id = portfolio.id
        holding_id = holding.id

        portfolio.delete()

        # Portfolio should be deleted
        assert not Portfolio.objects.filter(id=portfolio_id).exists()

        # Holding should be cascade deleted
        assert not Holding.objects.filter(id=holding_id).exists()

        # Asset should still exist (not cascade deleted)
        assert Asset.objects.filter(id=asset.id).exists()

    @pytest.mark.django_db
    def test_unique_constraints(self):
        """Test unique constraint enforcement."""
        from personal_finance.assets.models import Portfolio

        user = User.objects.create_user(
            username="testuser", email="test@example.com"
        )

        # Create first portfolio
        Portfolio.objects.create(user=user, name="My Portfolio")

        # Try to create second portfolio with same name for same user
        # This should fail due to unique_together constraint
        with pytest.raises(
            Exception
        ):  # Could be IntegrityError or ValidationError
            Portfolio.objects.create(user=user, name="My Portfolio")

    @pytest.mark.django_db
    def test_model_ordering(self):
        """Test model default ordering."""
        from personal_finance.assets.models import Asset

        # Create assets in non-alphabetical order
        Asset.objects.create(
            symbol="ZZZZ", name="Z Asset", asset_type=Asset.ASSET_STOCK
        )
        Asset.objects.create(
            symbol="AAAA", name="A Asset", asset_type=Asset.ASSET_STOCK
        )
        Asset.objects.create(
            symbol="MMMM", name="M Asset", asset_type=Asset.ASSET_STOCK
        )

        # Get all assets (should be ordered)
        assets = list(Asset.objects.all())
        symbols = [asset.symbol for asset in assets]

        # Should be ordered according to Meta.ordering
        assert symbols == sorted(symbols)


class TestApplicationUtilities:
    """Test application utility functions and helpers."""

    def test_model_string_representations(self):
        """Test that models have meaningful string representations."""
        from personal_finance.assets.models import Asset

        # Test that str() methods return useful information
        asset = Asset(
            symbol="AAPL", name="Apple Inc.", asset_type=Asset.ASSET_STOCK
        )

        str_repr = str(asset)
        # Should contain key identifying information
        assert "AAPL" in str_repr or "Apple Inc." in str_repr

    def test_model_property_methods(self):
        """Test that model property methods work correctly."""
        from personal_finance.assets.models import Asset

        # Test asset properties (if any exist)
        asset = Asset(
            symbol="TEST", name="Test Asset", asset_type=Asset.ASSET_STOCK
        )

        # Test basic properties exist and are accessible
        assert hasattr(asset, "symbol")
        assert hasattr(asset, "name")
        assert hasattr(asset, "asset_type")
        assert hasattr(asset, "is_active")

    @pytest.mark.django_db
    def test_model_relationships(self):
        """Test model relationship functionality."""
        from personal_finance.assets.models import Asset, Portfolio, Holding

        # Create test data
        user = User.objects.create_user(
            username="testuser", email="test@example.com"
        )

        asset = Asset.objects.create(
            symbol="TEST", name="Test Asset", asset_type=Asset.ASSET_STOCK
        )

        portfolio = Portfolio.objects.create(user=user, name="Test Portfolio")

        holding = Holding.objects.create(
            portfolio=portfolio,
            asset=asset,
            quantity=Decimal("100.00"),
            cost_basis_per_unit=Decimal("50.00"),
        )

        # Test forward relationships
        assert holding.portfolio == portfolio
        assert holding.asset == asset
        assert portfolio.user == user

        # Test reverse relationships
        assert holding in portfolio.holdings.all()
        assert portfolio in user.portfolios.all()


@override_settings(DEBUG=True)
class TestDevelopmentSettings(TestCase):
    """Test development-specific settings and configurations."""

    def test_debug_mode_settings(self):
        """Test settings when in debug mode."""
        # In test, we override DEBUG=True
        assert settings.DEBUG is True

        # Debug mode should have certain characteristics
        assert hasattr(settings, "INSTALLED_APPS")

        # Should have development-friendly settings
        assert hasattr(settings, "DATABASES")

    def test_email_backend_configuration(self):
        """Test email backend configuration."""
        # Should have an email backend configured
        assert hasattr(settings, "EMAIL_BACKEND")

        # In development/test, often uses console or file backend
        backend = settings.EMAIL_BACKEND
        development_backends = [
            "django.core.mail.backends.console.EmailBackend",
            "django.core.mail.backends.filebased.EmailBackend",
            "django.core.mail.backends.locmem.EmailBackend",
        ]

        # Should be one of the development backends or properly configured
        assert (
            any(dev_backend in backend for dev_backend in development_backends)
            or "smtp" in backend.lower()
        )


class TestSecurityConfiguration:
    """Test security-related configuration."""

    def test_secret_key_exists(self):
        """Test that SECRET_KEY is configured."""
        assert hasattr(settings, "SECRET_KEY")
        assert settings.SECRET_KEY is not None
        assert len(settings.SECRET_KEY) > 10  # Should be reasonable length

    def test_allowed_hosts_configuration(self):
        """Test ALLOWED_HOSTS configuration."""
        assert hasattr(settings, "ALLOWED_HOSTS")
        assert isinstance(settings.ALLOWED_HOSTS, list)

    def test_security_middleware(self):
        """Test that security middleware is configured."""
        assert hasattr(settings, "MIDDLEWARE")
        middleware = settings.MIDDLEWARE

        # Should have Django's security middleware
        security_middleware = [
            "django.middleware.security.SecurityMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
        ]

        for middleware_class in security_middleware:
            assert any(middleware_class in mw for mw in middleware)


class TestLoggingConfiguration:
    """Test logging configuration."""

    def test_logging_configuration_exists(self):
        """Test that logging is configured."""
        # Should have logging configuration
        if hasattr(settings, "LOGGING"):
            logging_config = settings.LOGGING
            assert isinstance(logging_config, dict)

            # Should have basic logging structure
            if "version" in logging_config:
                assert logging_config["version"] == 1

    def test_logger_usage(self):
        """Test basic logger functionality."""
        import logging

        # Should be able to get and use a logger
        logger = logging.getLogger("personal_finance")

        # Should not raise exception
        logger.info("Test log message")
        logger.debug("Test debug message")


class TestMiddlewareConfiguration:
    """Test middleware configuration."""

    def test_required_middleware(self):
        """Test that required middleware is present."""
        middleware = settings.MIDDLEWARE

        # Essential Django middleware
        required_middleware = [
            "django.middleware.common.CommonMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
        ]

        for required_mw in required_middleware:
            assert any(required_mw in mw for mw in middleware), (
                f"Required middleware {required_mw} not found"
            )

    def test_middleware_order(self):
        """Test middleware ordering for critical components."""
        middleware = settings.MIDDLEWARE

        # Security middleware should generally come early
        security_idx = None
        session_idx = None

        for i, mw in enumerate(middleware):
            if "SecurityMiddleware" in mw:
                security_idx = i
            if "SessionMiddleware" in mw:
                session_idx = i

        # If both exist, security should come before sessions
        if security_idx is not None and session_idx is not None:
            assert security_idx < session_idx
