---
description: 'Project-wide guidelines for Django-based personal finance application development with modern Python practices'
applyTo: '**'
---

# Personal Finance Application - Development Guidelines

This document provides comprehensive guidelines for developing the Personal Finance Django application. These instructions help GitHub Copilot and developers maintain consistency, quality, and best practices across the codebase.

## Project Context

- **Framework**: Django 5.2+ with modern Python 3.14+
- **Architecture**: Modular Django apps with REST API, WebSockets, and background tasks
- **Database**: PostgreSQL with Redis for caching and message broker
- **Key Technologies**: Django REST Framework, Django Channels, Celery, OpenTelemetry, Docker
- **Domain**: Personal finance management (portfolios, assets, holdings, transactions)

## Project Structure

```
personal-finance/
├── apps/                    # Django applications
│   ├── core/               # Core functionality, health checks
│   ├── users/              # User management, authentication
│   ├── assets/             # Assets, portfolios, holdings
│   └── api/                # REST API endpoints
├── config/                  # Django configuration
│   ├── settings/           # Environment-specific settings
│   └── urls.py             # Root URL configuration
├── templates/              # Django templates
│   ├── core/
│   └── assets/
├── tests/                  # Test suite
├── static/                 # Static files
└── deploy/                 # Deployment configurations
```

## General Instructions

### Django App Development

- **Modular Structure**: Each app in `apps/` should be self-contained with models, views, serializers, urls, and tests
- **App Organization**: Follow this structure within each app:
  ```
  app_name/
  ├── __init__.py
  ├── models.py          # Database models
  ├── views.py           # View functions/classes
  ├── serializers.py     # DRF serializers
  ├── urls.py            # URL patterns
  ├── admin.py           # Django admin configuration
  ├── apps.py            # App configuration
  └── tests/             # App-specific tests
  ```
- **Naming Convention**: Use lowercase with underscores for app names (e.g., `data_sources`, not `DataSources`)

### Code Style and Standards

- **Type Hints**: Always use type hints for function parameters and return values
  ```python
  from django.http import HttpRequest, HttpResponse

  def my_view(request: HttpRequest, item_id: int) -> HttpResponse:
      # Implementation
  ```
- **Modern Python**: Use Python 3.14+ features (union types with `|`, pattern matching, etc.)
- **Docstrings**: Use Google-style docstrings for modules, classes, and complex functions
- **Line Length**: Maximum 100 characters (enforced by ruff)
- **Import Order**: Standard library, third-party, Django, local (use ruff's isort integration)

## Django Best Practices

### Models

- **Verbose Names**: Always provide `verbose_name` and `verbose_name_plural` using `gettext_lazy`
- **Help Text**: Add `help_text` to fields for clarity in admin and API documentation
- **Field Choices**: Define choices as class constants with descriptive names
- **Meta Class**: Include ordering, indexes, and constraints in Meta class
- **String Representation**: Implement meaningful `__str__` methods

**Good Example:**
```python
from django.db import models
from django.utils.translation import gettext_lazy as _

class Asset(models.Model):
    """Financial asset model for storing asset metadata."""

    ASSET_STOCK = "STOCK"
    ASSET_TYPE_CHOICES = [
        (ASSET_STOCK, _("Stock")),
        # More choices...
    ]

    ticker = models.CharField(
        _("ticker symbol"),
        max_length=20,
        unique=True,
        db_index=True,
        help_text=_("The asset's ticker symbol (e.g., AAPL, BTC-USD)"),
    )

    class Meta:
        verbose_name = _("asset")
        verbose_name_plural = _("assets")
        ordering = ["ticker", "name"]
        indexes = [
            models.Index(fields=["ticker"]),
        ]

    def __str__(self) -> str:
        return f"{self.ticker} - {self.name}"
```

**Bad Example:**
```python
class Asset(models.Model):
    ticker = models.CharField(max_length=20)  # Missing verbose_name, help_text
    name = models.CharField(max_length=255)

    # Missing Meta class and __str__ method
```

### Views

- **Function-Based Views**: Prefer function-based views with decorators for simplicity
- **Authentication**: Use `@login_required` decorator for views requiring authentication
- **Type Hints**: Always type-hint request and return values
- **Query Optimization**: Use `select_related()` and `prefetch_related()` to avoid N+1 queries

**Good Example:**
```python
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render

@login_required
def portfolio_detail(request: HttpRequest, portfolio_id: int | None = None):
    """Display a user's portfolio with their holdings/assets."""
    portfolio = Portfolio.objects.filter(
        user=request.user,
        is_active=True
    ).first()

    holdings = portfolio.holdings.filter(
        is_active=True
    ).select_related('asset') if portfolio else []

    return render(request, 'assets/portfolio_detail.html', {
        'portfolio': portfolio,
        'holdings': holdings,
    })
```

### URLs

- **App Namespaces**: Use `app_name` in app-level URLs for namespacing
- **Naming**: Use descriptive, lowercase names with hyphens (e.g., `portfolio-detail`)
- **URL Patterns**: Use path converters for type safety (`<int:id>`, `<slug:slug>`)

**Good Example:**
```python
from django.urls import path
from . import views

app_name = "assets"

urlpatterns = [
    path("portfolio/", views.portfolio_detail, name="portfolio-detail"),
    path(
        "portfolio/<int:portfolio_id>/",
        views.portfolio_detail,
        name="portfolio-detail-id"
    ),
]
```

### REST API Development

- **Serializers**: Create explicit serializers in `serializers.py`
- **ViewSets**: Use DRF ViewSets for standard CRUD operations
- **Permissions**: Implement proper permission classes for API endpoints
- **Documentation**: Use `drf-spectacular` decorators for API documentation

**Good Example:**
```python
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

class AssetSerializer(serializers.ModelSerializer):
    """Serializer for Asset model."""

    class Meta:
        model = Asset
        fields = ['id', 'ticker', 'name', 'asset_type', 'currency']
        read_only_fields = ['id']

class AssetViewSet(ModelViewSet):
    """ViewSet for managing assets."""

    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['asset_type', 'currency']
```

## Testing Standards

### Test Organization

- **Location**: Place tests in `tests/` directory with structure mirroring `apps/`
- **Naming**: Use `test_*.py` pattern for test files
- **Test Classes**: Use Django's `TestCase` for database-dependent tests
- **Fixtures**: Define reusable fixtures in `conftest.py`

### Test Structure

- **Arrange-Act-Assert**: Follow AAA pattern in all tests
- **Test Names**: Use descriptive names that explain what is being tested
- **Setup**: Use `setUp()` method for common test data
- **Database**: Use Django's test database, not production

**Good Example:**
```python
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from apps.assets.models import Portfolio

class PortfolioDetailViewTest(TestCase):
    """Test portfolio detail view."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser', password='testpass'
        )
        self.client = Client()

    def test_portfolio_detail_view_requires_login(self):
        """Test that portfolio detail view requires authentication."""
        response = self.client.get(reverse('assets:portfolio-detail'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_portfolio_detail_view_with_portfolio(self):
        """Test portfolio detail view with a portfolio."""
        portfolio = Portfolio.objects.create(
            user=self.user,
            name='Test Portfolio'
        )
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('assets:portfolio-detail'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Portfolio', response.content)
```

## Security Best Practices

- **Authentication**: Always use Django's authentication system
- **CSRF Protection**: Ensure CSRF tokens in forms and AJAX requests
- **SQL Injection**: Use ORM queries, never raw SQL with user input
- **XSS Protection**: Use Django's auto-escaping in templates
- **Permissions**: Check user permissions before sensitive operations
- **Secrets**: Store secrets in environment variables, never in code

## Performance Optimization

### Database Queries

- **Query Optimization**: Use `select_related()` for foreign keys, `prefetch_related()` for many-to-many
- **Indexing**: Add database indexes for frequently queried fields
- **Pagination**: Use Django REST Framework's pagination for list endpoints
- **Bulk Operations**: Use `bulk_create()` and `bulk_update()` for multiple records

### Caching

- **Redis Cache**: Use Redis for caching frequently accessed data
- **Cache Keys**: Use descriptive, namespaced cache keys
- **Cache Invalidation**: Implement proper cache invalidation on updates

## Templates

### Template Structure

- **Base Template**: Extend from a base template for consistency
- **Block Structure**: Use named blocks for content, styles, and scripts
- **Static Files**: Use `{% load static %}` and `{% static 'path' %}` for assets
- **URL Resolution**: Use `{% url 'namespace:name' %}` instead of hardcoded paths

**Good Example:**
```django
{% extends "base.html" %}
{% load static %}

{% block title %}Portfolio - {{ portfolio.name }}{% endblock %}

{% block content %}
<div class="container">
    <h1>{{ portfolio.name }}</h1>
    <a href="{% url 'assets:portfolio-detail' %}">Back to Portfolios</a>
</div>
{% endblock %}
```

## Common Patterns

### Model Signals

Use signals for decoupled event handling:

```python
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Portfolio)
def handle_portfolio_created(sender, instance, created, **kwargs):
    """Handle portfolio creation."""
    if created:
        # Perform action on creation
        pass
```

### Custom Managers

Create custom managers for common queries:

```python
class ActivePortfolioManager(models.Manager):
    """Manager for active portfolios."""

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class Portfolio(models.Model):
    # Fields...
    objects = models.Manager()  # Default manager
    active = ActivePortfolioManager()  # Custom manager
```

### Celery Tasks

Define async tasks in `tasks.py`:

```python
from celery import shared_task

@shared_task
def calculate_portfolio_value(portfolio_id: int) -> dict:
    """Calculate portfolio value asynchronously."""
    portfolio = Portfolio.objects.get(id=portfolio_id)
    # Calculation logic
    return {'portfolio_id': portfolio_id, 'value': total_value}
```

## Validation and Verification

### Pre-Commit Hooks

All code must pass pre-commit checks:

```bash
# Run all pre-commit hooks
pre-commit run --all-files
```

### Django Checks

Verify Django configuration:

```bash
# Run Django system checks
uv run python manage.py check
```

### Migrations

Check for missing migrations:

```bash
# Create migrations
uv run python manage.py makemigrations

# Apply migrations
uv run python manage.py migrate
```

### Running Tests

Execute test suite:

```bash
# Run all tests
uv run python manage.py test

# Run specific test file
uv run python manage.py test tests.assets.test_views
```

## Tools and Utilities

- **Package Manager**: Use `uv` for dependency management
- **Linting**: `ruff` for code formatting and linting (configured in `pyproject.toml`)
- **Type Checking**: `mypy` for static type checking
- **Testing**: Django's test framework with `pytest-django` support
- **Database**: PostgreSQL for production, SQLite fallback for development
- **Cache**: Redis for caching and Celery message broker

## Domain-Specific Guidelines

### Financial Data

- **Decimal Fields**: Always use `DecimalField` for monetary values, never `FloatField`
- **Currency**: Store currency as ISO 4217 codes (USD, EUR, etc.)
- **Precision**: Use appropriate `max_digits` and `decimal_places` for financial calculations
- **Validation**: Validate financial data constraints (e.g., non-negative quantities)

**Good Example:**
```python
quantity = models.DecimalField(
    _("quantity"),
    max_digits=20,
    decimal_places=8,
    default=Decimal("0"),
    help_text=_("Number of shares/units held"),
)
```

### Asset Management

- **Identifiers**: Support multiple identifier types (ticker, ISIN, CUSIP, SEDOL)
- **Asset Types**: Use predefined choices for asset types
- **Markets**: Track primary market/exchange for each asset
- **Metadata**: Use JSONField for flexible additional data

## Maintenance and Updates

- **Dependencies**: Keep dependencies up to date using `uv sync --upgrade`
- **Security**: Run security audits with `pip-audit` or `safety`
- **Documentation**: Update docstrings and comments when code changes
- **Migrations**: Create migrations for model changes immediately
- **Tests**: Add tests for new features and bug fixes

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/en/5.2/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django Channels](https://channels.readthedocs.io/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

---

**Note**: These guidelines should be followed consistently across the codebase. When in doubt, refer to existing code patterns in the project or consult the official documentation for the relevant framework or library.
