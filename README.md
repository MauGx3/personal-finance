# Personal Finance

A Django project built with django-keel

## Features

- **Django 5.2** with Python 3.14
- **Package Management**: uv
- **Database**: postgresql
- **Cache**: Redis
- **API**: Django REST Framework
- **Frontend**: Next.js
- **WebSockets**: Django Channels
- **Authentication**: django-allauth + JWT
- **2FA**: TOTP-based two-factor authentication
- **Observability**: OpenTelemetry + Prometheus + Grafana + Sentry
- **Deployment**: Docker, Kubernetes

## Quick Start

### Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker and Docker Compose
- kubectl (for Kubernetes deployment)
- Helm 3+ (for Kubernetes deployment)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone github.com/maugx3/personal-finance
   cd personal_finance
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```
   3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Start development services**
   ```bash
   docker compose up -d
   ```

5. **Run migrations**
   ```bash
   uv run python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   uv run python manage.py createsuperuser
   ```

7. **Start development server**
   ```bash
   uv run python manage.py runserver
   ```
### Using Justfile (Recommended)

We provide a `Justfile` for common tasks:

```bash
# Install just: https://github.com/casey/just
just --list              # Show all available commands
just dev                 # Start development server
just test                # Run tests
just lint                # Run linters
just format              # Format code
just migrate             # Run migrations
just shell               # Open Django shell
```

## Project Structure

```
personal_finance/
├── apps/                      # Django applications
│   ├── core/                 # Core app (health checks, utils)
│   ├── users/                # User model and authentication
│   └── api/                  # API endpoints
├── config/                    # Project configuration
│   ├── settings/             # Split settings (base, dev, test, prod)
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── static/                    # Static files
├── media/                     # Media uploads
├── docs/                      # Documentation (MkDocs)
│   └── adr/                  # Architecture Decision Records
├── deploy/
│   └── k8s/                  # Kubernetes manifests
│       ├── helm/             # Helm charts
│       └── kustomize/        # Kustomize overlays
├── .github/
│   └── workflows/            # GitHub Actions
├── tests/                     # Test files
├── Dockerfile                 # Production Docker image
├── docker-compose.yml         # Development environment
├── Justfile                   # Task runner
├── pyproject.toml            # Python dependencies and config
└── README.md                 # This file
```

## Development

### Running Tests

```bash
just test
# or
uv run pytest
```

### Code Quality

```bash
# Format code
just format

# Lint code
just lint

# Type check
just typecheck
```

### Database Migrations

```bash
# Create migrations
just makemigrations

# Apply migrations
just migrate

# Check for migration issues
just migrate-check
```


## Deployment

Detailed deployment guides are available in `docs/deployment/`:

- **[Docker](docs/deployment/docker.md)**: Universal containerization
- **[Kubernetes](docs/deployment/kubernetes.md)**: Helm + Kustomize for GitOps

See [Deployment Overview](docs/deployment/overview.md) for platform comparison and decision guide.

## Documentation

Full documentation is available in the `docs/` directory and can be built with MkDocs:

```bash
just docs-serve
```

Visit http://localhost:8000 to view the documentation.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

Built with [django-keel](https://github.com/CuriousLearner/django-keel) 🚢
