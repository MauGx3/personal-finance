# Personal Finance

Welcome to the Personal Finance documentation!

## Overview

A Django project built with django-keel

## Features

### Core
- **Django 5.2** with Python 3.14
- **Package Management**: uv
- **Database**: postgresql with connection pooling
- **Caching**: Redis for high performance
- **Authentication**: django-allauth + JWT
- **Two-Factor Authentication**: TOTP-based (Google Authenticator, Authy)
### API & Frontend
- **API Framework**: Django REST Framework with OpenAPI/Swagger docs
- **Frontend**: Next.js (TypeScript, App Router)
### Background Tasks & Real-time
- **WebSockets**: Django Channels for real-time features
- **Real-time Updates**: Live notifications, chat, collaborative editing
### SaaS Features
- **Feature Flags**: django-waffle for A/B testing and gradual rollouts
- **User Impersonation**: Staff can impersonate users for support/debugging

### Observability & Monitoring
- **Error Tracking**: Sentry + distributed tracing
- **Structured Logging**: JSON logs with correlation IDs
- **Metrics**: Prometheus + Grafana dashboards
- **Tracing**: OpenTelemetry for distributed tracing
- **APM**: Application Performance Monitoring
- **Health Checks**: `/health/` endpoint with database connectivity checks
### Security
- **Security Headers**: CSP, HSTS, X-Frame-Options
- **Password Security**: Argon2 hashing
- **CSRF Protection**: Built-in Django CSRF + SameSite cookies
- **Secret Management**: SOPS for encrypted configuration
### Development Tools
- **Task Runner**: Justfile for common commands
- **Code Quality**: Ruff for linting and formatting
- **Type Checking**: mypy for static type analysis
- **Testing**: pytest with coverage reporting
- **Pre-commit Hooks**: Automated code quality checks
- **CI/CD**: GitHub Actions
### Deployment
- **Docker**: Multi-stage builds for production deployment
- **Kubernetes**: Helm charts + Kustomize overlays for GitOps
- **Production Ready**: Environment-based configuration, database migrations, static file serving

## Quick Start

```bash
# Clone the repository
git clone
cd personal_finance

# Install dependencies
uv sync


# Start development services
docker compose up -d

# Run migrations
just migrate

# Create superuser
just createsuperuser

# Start development server
just dev
```

## Access Points

After starting the development server:

- **Application**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/api/schema/swagger/
- **Email Testing (Mailpit)**: http://localhost:8025
## Next Steps

- [Installation Guide](getting-started/installation.md) - Detailed setup instructions
- [Architecture Overview](architecture/overview.md) - System design and structure
- [Development Guide](development/testing.md) - Testing and development workflow
- [Deployment](deployment/) - Production deployment guides

## Documentation

Browse the full documentation:

- **Getting Started**: Installation, configuration, first steps
- **Architecture**: System design, project structure, key decisions
- **Development**: Testing, debugging, workflow
- **Deployment**: Platform-specific deployment guides
- **ADRs**: Architecture Decision Records

---

**Built with [Django Keel](https://github.com/CuriousLearner/django-keel)** 🚢
