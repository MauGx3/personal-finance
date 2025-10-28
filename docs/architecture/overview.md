# Architecture Overview

Personal Finance follows a modern Django architecture with clean separation of concerns and production-ready patterns.

## Project Structure

```
personal_finance/
├── apps/                   # Django applications
│   ├── core/              # Core functionality (health checks, utils, middleware)
│   ├── users/             # Custom user model and authentication
│   ├── api/               # API endpoints (DRF)
│   └── ...                # Additional apps as needed
├── config/                 # Project configuration
│   ├── settings/          # Split settings (base, dev, test, prod)
│   ├── urls.py            # URL configuration
│   ├── asgi.py            # ASGI application (Django Channels)
│   └── wsgi.py            # WSGI application
├── static/                 # Static files (CSS, JS, images)
├── media/                  # User uploads
├── docs/                   # Project documentation
│   └── adr/               # Architecture Decision Records
├── tests/                  # Test suite
├── deploy/                 # Deployment configurations
│   └── k8s/               # Kubernetes (Helm + Kustomize)
├── .github/
│   └── workflows/         # GitHub Actions CI/CD
├── Dockerfile             # Production container image
├── docker-compose.yml     # Development environment
├── Justfile               # Task runner (commands)
├── pyproject.toml         # Python dependencies and tool config
└── README.md
```

## Key Components

### Django Apps

- **core**: Core functionality shared across the project
  - Health check endpoints (`/health/`)
  - Middleware (security, logging)
  - Utility functions and helpers
- **users**: Custom user model and authentication
  - Email-based authentication
  - User profile management
- Social authentication (Google, GitHub, etc.)
- Two-factor authentication (TOTP)
- User impersonation for staff support

- **api**: API layer
- RESTful endpoints (Django REST Framework)
  - OpenAPI/Swagger documentation
  - Serializers and viewsets
- Authentication (JWT tokens)
  - Permissions and throttling

### Settings Architecture

Settings are environment-specific and split across files:

- **`base.py`**: Common settings for all environments
  - Installed apps and middleware
  - Database and cache configuration
  - Static and media file handling
  - Security settings (CSRF, headers, allowed hosts)

- **`dev.py`**: Development overrides
  - `DEBUG = True`
  - Django Debug Toolbar
  - Permissive CORS for local frontend development
  - Email backend → Mailpit (console)

- **`test.py`**: Test configuration
  - In-memory database for speed
  - Disabled migrations where safe
  - Test-specific settings

- **`prod.py`**: Production hardening
  - `DEBUG = False`
  - Strict security headers (CSP, HSTS)
  - Gunicorn WSGI server
- Sentry error tracking
- OpenTelemetry tracing
### Deployment

#### Docker (Universal)
- **Build**: Multi-stage Dockerfile (production-optimized)
- **Compose**: Development environment setup
- **Images**: Optimized layers, minimal attack surface
- **Best for**: Portability, any cloud provider

#### Kubernetes (Enterprise)
- **Charts**: Helm for templated deployments
- **Overlays**: Kustomize for environment-specific configs
- **Features**: HPA, ingress, service mesh ready
- **Database**: CloudNativePG operator for PostgreSQL
- **Monitoring**: Prometheus + Grafana stack
- **Best for**: Enterprise scale, multi-cluster, advanced orchestration

## Data Flow

### Request/Response Flow

```
User Request
     ↓
Load Balancer (ALB/Ingress)
     ↓
Django Middleware Stack
     ├─ SecurityMiddleware (headers, SSL redirect)
     ├─ SessionMiddleware (session management)
     ├─ AuthenticationMiddleware (user authentication)
└─ WaffleMiddleware (feature flags)
     ↓
URL Router
     ↓
View / API Endpoint
     ├─ Permission Checks
├─ Business Logic
     ├─ Database Queries (PostgreSQL)
├─ Cache Lookups (Redis)
↓
Serialization / Template Rendering
     ↓
Response (JSON / HTML)
```

## Security Architecture

### Authentication & Authorization

1. **User Authentication**
- Session-based (django-allauth)
   - Token-based (JWT for API)
- Two-factor authentication (TOTP)
2. **Authorization**
- Django permissions system
   - Custom decorators for view protection

3. **Security Headers**
   - Content Security Policy (CSP)
   - HTTP Strict Transport Security (HSTS)
   - X-Frame-Options (Clickjacking protection)
   - X-Content-Type-Options (MIME sniffing protection)
4. **Input Validation**
   - Django form validation
- DRF serializer validation
- CSRF token protection
## Database Design

### Core Tables

- `users_user`: Custom user model (email-based)
- `waffle_*`: Feature flag tables

### Indexing Strategy

- Foreign keys automatically indexed
- Email fields (unique + indexed)
- Composite indexes for common query patterns

## Observability

### Logging
- **Format**: Structured JSON logs
- **Levels**: DEBUG → INFO → WARNING → ERROR → CRITICAL
- **Context**: Request ID, user ID
- **Aggregation**: OpenTelemetry → Logging backend
### Monitoring
- **Error Tracking**: Sentry (real-time error alerts)
- **Metrics**: Prometheus (custom metrics + Django metrics)
- **Dashboards**: Grafana (pre-built dashboards)
- **Tracing**: OpenTelemetry (distributed request tracing)
- **APM**: Application performance monitoring
- **Health Checks**: `/health/` endpoint (database, cache, Redis)

## Performance Optimization

### Caching Strategy
- **Backend**: Redis
- **Cached Data**:
  - Database query results (per-view caching)
  - API responses (DRF throttling)
- Template fragments
- **Cache Invalidation**: Signals on model save/delete
### Database Optimization
- Connection pooling (production)
- Select/prefetch related for N+1 prevention
- Database indexes on frequently queried fields
- Query optimization with Django Debug Toolbar (dev)

### Static Files
- **Storage**: Local filesystem (development)
- **Production**: WhiteNoise for efficient static serving
- **Compression**: Gzip/Brotli enabled
- **Cache Headers**: Long expiry for static assets

## Design Decisions

### Why Split Settings?
- **Environment isolation**: Dev settings differ from prod
- **Security**: Secrets never in version control
- **Flexibility**: Easy to override per-environment
- **Testing**: Optimized test configuration

### Why Custom User Model?
- **Email-based**: More modern than username
- **Future-proof**: Easy to extend without migrations
- **Django best practice**: Recommended in official docs

### Why uv over Poetry?
- **Speed**: 10-100x faster dependency resolution
- **Simplicity**: Single binary, no Python dependency
- **Standards**: Uses pyproject.toml (PEP 621)
- **Compatibility**: Works with existing Poetry projects
### Why Helm + Kustomize?
- **Helm**: Package management, versioning, rollbacks
- **Kustomize**: Environment-specific configs (GitOps-friendly)
- **Together**: Best of both worlds (templating + patching)
## Architecture Decision Records

For detailed explanations of key architectural choices, see:

- [ADR Directory](../adr/)
- Each ADR documents: Context, Decision, Consequences, Alternatives

## Further Reading

- [Getting Started](../getting-started/installation.md)
- [Development Guide](../development/testing.md)
- [Deployment Guides](../deployment/)
