# System Patterns

## Architecture Overview

### Django Project Structure

```
personal-finance/
├── apps/                    # Django apps (modular features)
│   ├── assets/             # Asset management (✅ Complete)
│   │   ├── models.py       # Asset, Portfolio, Holding models
│   │   ├── admin.py        # Django admin configuration
│   │   ├── serializers.py  # DRF API serializers
│   │   ├── tests/          # Unit tests
│   │   └── migrations/     # Database migrations
│   ├── core/               # Core utilities and base classes
│   └── users/              # User management extensions
├── config/                  # Django settings and configuration
│   ├── settings/           # Environment-specific settings
│   │   ├── base.py        # Shared settings
│   │   ├── local.py       # Development settings
│   │   └── production.py  # Production settings
│   ├── urls.py            # Root URL configuration
│   ├── asgi.py            # ASGI entrypoint
│   └── wsgi.py            # WSGI entrypoint
├── templates/              # Django templates
├── static/                 # Static assets (CSS, JS, images)
├── media/                  # User-uploaded files
├── tests/                  # Integration tests
└── manage.py              # Django management CLI
```

## Key Technical Decisions

### 1. Financial Precision

**Decision**: Use `DecimalField` for all financial values

**Rationale**:

- Floating-point arithmetic introduces rounding errors
- Financial calculations require exact precision
- Example: 0.1 + 0.2 = 0.30000000000000004 in float (WRONG)
- Decimal avoids these issues: Decimal("0.1") + Decimal("0.2") = Decimal("0.3") (CORRECT)

**Implementation**:

```python
# All financial fields use Decimal
quantity = models.DecimalField(max_digits=20, decimal_places=8)
average_price = models.DecimalField(max_digits=20, decimal_places=8)

# Always use Decimal in calculations
total_cost = self.quantity * self.average_price  # Returns Decimal
```

**Pattern**: Never use FloatField for money, quantities, or prices.

### 2. Data Integrity via Database Constraints

**Decision**: Enforce business rules at the database level

**Rationale**:

- Prevents invalid data even if application logic has bugs
- Ensures consistency across multiple application instances
- Provides clear error messages when violations occur

**Implementation**:

```python
class Meta:
    constraints = [
        # Prevent duplicate holdings
        models.UniqueConstraint(
            fields=["user", "asset", "portfolio"],
            name="unique_user_asset_portfolio_holding",
        ),
        # Ensure positive quantities
        models.CheckConstraint(
            check=models.Q(quantity__gte=0),
            name="quantity_non_negative",
        ),
    ]
```

**Pattern**: Use UniqueConstraint, CheckConstraint, and database-level validation.

### 3. Soft Deletion Pattern

**Decision**: Use `is_active` boolean field instead of hard deletes

**Rationale**:

- Preserves historical data for auditing
- Allows "undelete" functionality
- Maintains referential integrity
- Useful for reporting and analytics

**Implementation**:

```python
is_active = models.BooleanField(
    default=True,
    help_text="Whether this asset is still active"
)

# Query active assets
Asset.objects.filter(is_active=True)
```

**Pattern**: Add is_active to models that users might want to "delete" but preserve.

### 4. Automatic Timestamp Tracking

**Decision**: Add created_at and updated_at to all models

**Rationale**:

- Track when records were created and last modified
- Useful for debugging and auditing
- Enables time-based queries
- No manual timestamp management needed

**Implementation**:

```python
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
```

**Pattern**: Include on every model, mark as read-only in admin.

### 5. Flexible Metadata Storage

**Decision**: Use JSONField for extensible attributes

**Rationale**:

- Asset-specific data varies widely (dividends, splits, options, etc.)
- Avoids adding many rarely-used columns
- Enables quick prototyping of new features
- PostgreSQL JSONField is efficient and queryable

**Implementation**:

```python
metadata = models.JSONField(
    default=dict,
    blank=True,
    help_text="Additional metadata stored as JSON"
)

# Usage
asset.metadata = {"dividend_yield": "2.5%", "ex_dividend_date": "2025-11-15"}
```

**Pattern**: Use for optional, variable, or experimental data.

### 6. Related Name Pattern

**Decision**: Use descriptive `related_name` for ForeignKey relationships

**Rationale**:

- Makes reverse queries intuitive: `user.holdings.all()`
- Avoids Django's auto-generated names like `holding_set`
- Self-documenting code

**Implementation**:

```python
user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="holdings",  # user.holdings.all()
)
```

**Pattern**: Always specify related_name, use plural for many-to-one.

### 7. Computed Properties

**Decision**: Use @property for derived values

**Rationale**:

- Encapsulates calculation logic
- Provides clean API: `holding.total_cost_basis`
- Easy to test and modify
- No database storage needed

**Implementation**:

```python
@property
def total_cost_basis(self) -> Decimal:
    """Computed total cost basis."""
    if self.average_price is None or self.quantity is None:
        return Decimal("0")
    return self.quantity * self.average_price
```

**Pattern**: Use for calculations that depend on model fields.

### 8. API Serializer Separation

**Decision**: Different serializers for list, detail, and create operations

**Rationale**:

- List views need minimal fields for performance
- Detail views include related objects and computed fields
- Create views need validation but not read-only fields
- Reduces over-fetching and improves response times

**Implementation**:

```python
AssetListSerializer      # Lightweight for lists
AssetSerializer          # Full detail with relationships
AssetCreateSerializer    # Input validation for creation
```

**Pattern**: Create separate serializers for different use cases.

### 9. Queryset Optimization

**Decision**: Use select_related() in admin and API views

**Rationale**:

- Prevents N+1 query problems
- Single database query instead of one per related object
- Significant performance improvement for list views

**Implementation**:

```python
def get_queryset(self, request):
    return super().get_queryset(request).select_related(
        "user", "asset", "portfolio"
    )
```

**Pattern**: Always optimize querysets with select_related/prefetch_related.

### 10. Validation at Multiple Levels

**Decision**: Validate data at model, serializer, and database levels

**Rationale**:

- Defense in depth: multiple layers catch different errors
- Model validation: business logic (e.g., positive prices)
- Serializer validation: API input (e.g., regex patterns)
- Database constraints: data integrity (e.g., uniqueness)

**Implementation**:

```python
# Model validation
def clean(self):
    if self.quantity <= 0:
        raise ValidationError("Quantity must be positive")

# Serializer validation
def validate_ticker(self, value):
    if not re.match(r'^[A-Z0-9\-_.]+$', value):
        raise serializers.ValidationError("Invalid ticker format")

# Database constraint
models.CheckConstraint(check=models.Q(quantity__gte=0))
```

**Pattern**: Validate at all levels for maximum safety.

## Component Relationships

### Data Flow: Asset Management

```
User Authentication (Django Allauth)
    ↓
Django Admin Interface / REST API
    ↓
Django Views / DRF ViewSets
    ↓
Serializers (validation)
    ↓
Models (business logic)
    ↓
PostgreSQL Database (constraints)
```

### Model Relationships

```
User (Django auth)
    ↓ One-to-Many
Portfolio (user's portfolio grouping)
    ↓ One-to-Many
Holding (individual positions)
    ↓ Many-to-One
Asset (catalog entry)
```

## Design Patterns in Use

### 1. Fat Models, Thin Views

- Business logic lives in models (e.g., `total_cost_basis` calculation)
- Views/ViewSets handle HTTP concerns only
- Keeps logic reusable and testable

### 2. Repository Pattern (via Django ORM)

- Models serve as repositories for data access
- QuerySets provide abstraction over SQL
- Managers can be customized for complex queries

### 3. Serializer Pattern (DRF)

- Separates presentation from data
- Handles validation and transformation
- Different serializers for different contexts

### 4. Admin Pattern (Django Admin)

- Auto-generated CRUD interface
- Customizable via Admin classes
- Suitable for internal tools and data management

### 5. Settings Pattern

- Base settings with environment-specific overrides
- Keeps secrets out of code (use environment variables)
- Easy to maintain per-environment configuration

## Future Patterns to Implement

### 1. Service Layer

When business logic grows complex, introduce service classes:

```python
class PortfolioService:
    def calculate_performance(self, portfolio, start_date, end_date):
        # Complex calculation involving multiple models
        pass
```

### 2. Task Queue (Celery)

For async operations like price updates:

```python
@shared_task
def update_asset_prices():
    # Fetch latest prices from API
    # Update holdings' current values
    pass
```

### 3. WebSocket Consumers

For real-time updates:

```python
class PriceConsumer(AsyncWebsocketConsumer):
    async def send_price_update(self, price_data):
        # Send real-time price to connected clients
        pass
```

### 4. Event Sourcing

For transaction history and audit trail:

```python
class TransactionEvent(models.Model):
    event_type = models.CharField()  # BUY, SELL, DIVIDEND, SPLIT
    timestamp = models.DateTimeField()
    data = models.JSONField()
```

### 5. Read Model / Write Model (CQRS)

If read and write patterns diverge:

```python
# Write model: transactional
Transaction.objects.create(...)

# Read model: denormalized for fast queries
PortfolioSnapshot.objects.filter(date=today)
```

## Testing Patterns

### Current

- Unit tests for models using Django TestCase
- Focus on business logic and calculations
- Mock external dependencies (no network calls)

### Future

- Integration tests for API endpoints
- Performance tests for query optimization
- End-to-end tests for critical user flows
- Load testing for concurrent users

## Documentation Patterns

- Docstrings on all models, methods, and properties
- Type hints for clarity (e.g., `-> Decimal`)
- Comments for complex business logic
- README files in each app directory
- Memory bank for high-level context

## Key Principles

1. **Financial Precision**: Always use Decimal, never float
2. **Data Integrity**: Enforce at database level
3. **Performance**: Optimize querysets, use indexes
4. **Security**: User isolation, proper authentication
5. **Testability**: Write tests for all business logic
6. **Maintainability**: Follow Django conventions
7. **Extensibility**: Plan for future features
8. **Documentation**: Code should be self-explanatory
