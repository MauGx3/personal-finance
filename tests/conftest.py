import os
import sys
from pathlib import Path

import django
import pytest
from django.conf import settings

# Ensure the repository root is preferred on sys.path so files under
# `personal_finance/` in the repo root are loaded first. If a `src/`
# implementation exists we add it after the repo root so those modules
# remain discoverable without hiding repo-root modules such as
# `personal_finance/assets/models.py`.
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

# Put repo root first
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Make src/ discoverable but do not let it shadow repo-root modules
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))


def pytest_configure():
    """Configure pytest to work with Django."""
    # Set Django settings module
    # Ensure tests use the dedicated test settings (in-memory DB, simplified
    # apps)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
    # Call django.setup() so module-level imports that reference Django apps
    # (for example get_user_model()) do not raise AppRegistryNotReady during
    # collection. pytest-django will still manage test DB creation and
    # migrations when running tests.
    if not settings.configured:
        django.setup()

    # If a local virtualenv exists at .venv, ensure its bin/ is on PATH so
    # CLI dev tools (mypy, ruff, etc.) are discoverable by subprocess calls
    # inside tests that check for their presence.
    try:
        venv_bin = ROOT.joinpath(".venv", "bin")
        if venv_bin.exists():
            os.environ.setdefault("PATH", os.environ.get("PATH", ""))
            path_parts = os.environ["PATH"].split(os.pathsep)
            venv_bin_str = str(venv_bin)
            if venv_bin_str not in path_parts:
                # Prepend so the venv's tools take precedence
                path_parts.insert(0, venv_bin_str)
                os.environ["PATH"] = os.pathsep.join(path_parts)
    except Exception:
        # Non-fatal; tests will either import modules or the checks will fail
        # and report missing tooling as before.
        pass

    # Let pytest-django manage test database creation and migrations.
    # Running migrations manually here was causing persistent DB state and
    # interference between tests (leftover rows, UNIQUE constraint errors).
    # The test settings already point to a file-backed DB
    # (config.settings.test) which pytest-django will create/teardown
    # for the test session.
    # Keep this function focused on lightweight bootstrap tasks only.

    # Some legacy tests reference TestCase without importing it. Make it
    # available as a builtin to avoid NameError during test collection.
    try:
        import builtins

        from django.test import TestCase

        builtins.TestCase = TestCase
    except Exception:
        # If something goes wrong, don't block test collection here; the
        # underlying error will surface during test execution.
        pass


@pytest.fixture
def asset_factory():
    """Factory for creating test assets."""

    def _create_asset(**kwargs):
        from personal_finance.assets.models import Asset

        defaults = {
            "symbol": "TEST",
            "name": "Test Asset",
            "asset_type": Asset.ASSET_STOCK,
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
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
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
            "name": "Test Portfolio",
            "user": user,
        }
        defaults.update(kwargs)
        return Portfolio.objects.create(**defaults)

    return _create_portfolio


@pytest.fixture
def holding_factory(portfolio_factory, asset_factory):
    """Factory for creating test holdings."""

    def _create_holding(portfolio=None, asset=None, **kwargs):
        from decimal import Decimal

        from personal_finance.assets.models import Holding

        if portfolio is None:
            portfolio = portfolio_factory()
        if asset is None:
            asset = asset_factory()

        defaults = {
            "portfolio": portfolio,
            "asset": asset,
            "quantity": Decimal("100.00"),
            "cost_basis_per_unit": Decimal("50.00"),
        }
        defaults.update(kwargs)
        return Holding.objects.create(**defaults)

    return _create_holding
