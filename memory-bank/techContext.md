# Tech Context

## Technologies Used

### Core Framework

- **Django 4.2.24+** - Web framework with ORM, admin, and middleware
  - LTS version for long-term support
  - Secure, battle-tested, extensive ecosystem
  - Built-in admin interface for rapid CRUD
  - ORM for database abstraction

### Database

- **PostgreSQL** - Primary relational database
  - Advanced data types (JSONField, ArrayField)
  - Full ACID compliance
  - Excellent performance and scalability
  - Robust constraint enforcement
  - PostGIS available for geospatial features (future)

### API Framework

- **Django REST Framework (DRF)** - REST API toolkit
  - Serializers for data validation and transformation
  - Viewsets for CRUD operations
  - Authentication and permissions
  - Automatic OpenAPI/Swagger documentation
  - Browsable API for development

### Authentication

- **Django Allauth** - User authentication system
  - Email/password authentication
  - Social authentication support (future)
  - Email verification
  - Password reset flows
  - User registration

### Package Management

- **uv** - Fast Python package manager
  - Written in Rust for speed
  - Drop-in replacement for pip/pip-tools
  - Extremely fast dependency resolution
  - Reliable lock files for reproducible builds
  - Command pattern: `uv run python manage.py <command>`

### Testing

- **Django TestCase** - Built-in testing framework
  - Database transaction rollback for speed
  - Test client for simulating requests
  - Assertion helpers for Django-specific tests
  - Fixtures for test data

### Task Queue (Future)

- **Celery** - Distributed task queue
  - Async price updates
  - Scheduled periodic tasks
  - Background processing
  - Redis as message broker

### WebSockets (Future)

- **Django Channels** - ASGI/WebSocket support
  - Real-time price updates
  - Live portfolio value changes
  - Async consumers for WebSocket handling

## Development Setup

### Required Software

- Python 3.9+
- PostgreSQL 12+
- uv package manager
- Git

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/personal_finance

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email (future)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Local Development Commands

#### Project Setup

```bash
# Clone repository
git clone https://github.com/MauGx3/personal-finance.git
cd personal-finance

# Install dependencies with uv
uv sync

# Create database
createdb personal_finance

# Run migrations
uv run python manage.py migrate

# Create superuser
uv run python manage.py createsuperuser

# Run development server
uv run python manage.py runserver
```

#### Common Development Tasks

```bash
# Run tests
uv run python manage.py test

# Create migrations
uv run python manage.py makemigrations

# Apply migrations
uv run python manage.py migrate

# Django shell
uv run python manage.py shell

# Collect static files
uv run python manage.py collectstatic

# Check for issues
uv run python manage.py check
```

#### Database Operations

```bash
# Django shell for queries
uv run python manage.py shell -c "
from apps.assets.models import Asset
assets = Asset.objects.all()
for asset in assets:
    print(f'{asset.ticker}: {asset.name}')
"

# Database backup
pg_dump personal_finance > backup.sql

# Database restore
psql personal_finance < backup.sql
```

## Technical Constraints

### Python Version

- **Minimum**: Python 3.9
- **Recommended**: Python 3.11+
- **Rationale**: Django 4.2 requires 3.9+, newer versions have performance improvements

### Database Requirements

- **PostgreSQL only**: No SQLite or MySQL support
- **Rationale**: Need JSONField, advanced constraints, better performance
- **Version**: PostgreSQL 12+ for full JSON support

### Decimal Precision

- **All financial values**: DecimalField with max_digits=20, decimal_places=8
- **No floats allowed**: Enforced by linting and code review
- **Rationale**: Financial accuracy requires exact decimal arithmetic

### API Design

- **RESTful conventions**: Use HTTP verbs (GET, POST, PUT, DELETE) correctly
- **JSON only**: No XML or other formats
- **Authentication required**: All endpoints need auth (except public docs)
- **Versioning**: Use URL versioning (e.g., `/api/v1/`) for breaking changes

## Dependencies

### Core Dependencies (Production)

```
Django>=4.2.24
djangorestframework>=3.14.0
django-allauth>=0.57.0
psycopg>=3.1.0
python-decouple>=3.8
```

### Development Dependencies

```
django-extensions>=3.2.0
django-debug-toolbar>=4.2.0
ipython>=8.12.0
```

### Future Dependencies

```
celery>=5.3.0           # Task queue
redis>=5.0.0            # Message broker for Celery
channels>=4.0.0         # WebSocket support
yfinance>=0.2.0         # Financial data API
pandas>=2.0.0           # Data analysis
```

## Development Tools

### Code Quality

- **Linting**: Ruff or Flake8 for Python style
- **Formatting**: Black for consistent code style
- **Type Checking**: Pyright (currently showing warnings, can be improved)
- **Pre-commit hooks**: Format and lint before commits

### IDE Setup

- **VS Code**: Recommended editor
- **Extensions**: Python, Django, GitLens
- **Settings**: Auto-format on save, linter integration
- **Debugging**: Django debug configurations

### Version Control

- **Git**: Version control
- **Branch Strategy**:
  - `main`: Production-ready code
  - `new-codebase-structure`: Active development
  - Feature branches: `feature/<name>`
  - Bugfix branches: `bugfix/<name>`
- **Commit Convention**: Conventional commits (feat, fix, docs, refactor, etc.)

## Deployment Architecture (Future)

### Container Strategy

- **Docker**: Containerized application
- **docker-compose**: Local development and testing
- **Dockerfile**: Multi-stage builds for optimization
- **Images**: Separate containers for web, celery, redis

### Production Stack

- **Web Server**: Gunicorn with multiple workers
- **Reverse Proxy**: Nginx for static files and SSL termination
- **Database**: Managed PostgreSQL (AWS RDS, Google Cloud SQL, or similar)
- **Cache**: Redis for session storage and Celery broker
- **Static Files**: CDN or S3 for production static assets
- **Monitoring**: Application Performance Monitoring (APM) tool

### Hosting Options

- **AWS**: EC2 + RDS + ElastiCache + S3
- **Google Cloud**: Cloud Run + Cloud SQL + Cloud Storage
- **Heroku**: Simple deployment with add-ons
- **DigitalOcean**: App Platform or Droplets

## Performance Considerations

### Database Optimization

- **Indexes**: Added on frequently queried fields (ticker, user_id, etc.)
- **select_related**: For ForeignKey joins
- **prefetch_related**: For reverse ForeignKey and ManyToMany
- **Database pooling**: pgbouncer for connection management

### API Optimization

- **Pagination**: Limit large result sets
- **Field selection**: Use different serializers for list vs detail
- **Caching**: Redis for frequently accessed data (future)
- **Rate limiting**: Throttle API requests per user

### Frontend Optimization (Future)

- **Static assets**: Compressed and minified
- **CDN**: Serve from edge locations
- **Lazy loading**: Load images and data on demand
- **WebSockets**: Reduce HTTP overhead for real-time data

## Security Practices

### Current

- **HTTPS only**: In production
- **CSRF protection**: Django built-in
- **SQL injection**: ORM prevents by default
- **XSS protection**: Django template auto-escaping
- **Password hashing**: Django's PBKDF2 by default
- **Admin access**: Restricted by authentication

### Future

- **API authentication**: Token-based (JWT or DRF tokens)
- **Rate limiting**: Prevent abuse
- **Audit logging**: Track sensitive operations
- **Encryption at rest**: Database-level encryption
- **Regular updates**: Keep dependencies current

## Testing Strategy

### Current

- **Unit tests**: Model logic and calculations
- **Coverage**: 7 tests passing, expanding coverage
- **Test database**: Separate from development
- **Fixtures**: Minimal, prefer factory pattern

### Future

- **Integration tests**: API endpoints
- **End-to-end tests**: Critical user flows
- **Performance tests**: Load testing with locust
- **Security tests**: OWASP compliance scanning
- **CI/CD**: Automated testing on every commit

## Monitoring & Logging (Future)

### Application Monitoring

- **APM**: New Relic, Datadog, or Sentry
- **Error tracking**: Automatic error reports
- **Performance**: Track slow queries and endpoints
- **User analytics**: Usage patterns and feature adoption

### Logging

- **Structured logging**: JSON format for parsing
- **Log levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log aggregation**: Centralized logging service
- **Retention**: Keep logs for compliance and debugging

## Known Technical Issues

1. **Type checking warnings**: Pyright shows warnings for Django dynamic attributes
   - Not critical, can be suppressed with type: ignore or --extend-ignore
2. **No pricing API yet**: Placeholder methods return Decimal("0.00")
   - Planned for Phase 3
3. **No API viewsets**: Serializers exist but not wired to URLs
   - Planned for immediate next steps
4. **No authentication on API**: Need to add permissions
   - Planned with viewset implementation

## Technology Decision Log

### Why Django?

- Mature, well-documented framework
- Built-in admin saves development time
- Strong ORM with PostgreSQL support
- Large ecosystem of packages
- **Alternative considered**: FastAPI (chose Django for admin and maturity)

### Why PostgreSQL?

- Advanced features (JSON, constraints, indexes)
- Excellent performance and reliability
- Strong Django integration
- Industry standard for financial data
- **Alternative considered**: MySQL (chose PostgreSQL for features)

### Why uv?

- 10-100x faster than pip
- Reliable dependency resolution
- Modern, actively maintained
- Great developer experience
- **Alternative considered**: poetry (chose uv for speed)

### Why DRF?

- De facto standard for Django APIs
- Comprehensive feature set
- Great documentation
- Active community
- **Alternative considered**: Django Ninja (chose DRF for maturity)

### Why Decimal over Float?

- Financial precision requirement
- Avoids floating-point errors
- Industry best practice
- **Not negotiable**: This is a hard requirement

## Future Technology Additions

1. **Celery + Redis**: Async task processing for price updates
2. **Django Channels**: WebSocket support for real-time features
3. **yfinance or Alpha Vantage**: Financial data API
4. **pandas**: Data analysis and calculations
5. **matplotlib/plotly**: Charts and visualizations
6. **django-import-export**: CSV/Excel import/export
7. **django-filter**: Advanced API filtering
8. **drf-spectacular**: Enhanced OpenAPI documentation
9. **pytest**: More flexible testing framework
10. **Coverage.py**: Test coverage reporting
