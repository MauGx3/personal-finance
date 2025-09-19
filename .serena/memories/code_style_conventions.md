# Code Style and Conventions

## Code Style
- **Linter/Formatter**: Ruff (configured in pyproject.toml and pre-commit)
- **Line Length**: 79 characters (configured in pyproject.toml)
- **Python Version**: 3.11+ target, 3.13 in use
- **Import Style**: Follow Django conventions with absolute imports
- **Type Hints**: Encouraged for new code

## Pre-commit Hooks
- Ruff (linting and formatting)
- Django-upgrade for Django-specific improvements
- djLint for Django template formatting
- Standard pre-commit hooks (trailing whitespace, JSON/YAML validation, etc.)

## Naming Conventions
- **Files**: snake_case for Python files
- **Classes**: PascalCase (Django standard)
- **Functions/Variables**: snake_case
- **Constants**: UPPER_SNAKE_CASE
- **Django Apps**: snake_case

## Security Guidelines
- Never commit secrets or credentials
- Use environment variables for configuration
- Avoid hardcoded database URLs
- **Security Issue**: Binding to 0.0.0.0 (all interfaces) should be avoided in local development

## Django Specifics
- Follow Django project structure with apps
- Use Django settings patterns (base/local/production)
- Migrations handled via Alembic (hybrid approach)
- Model definitions follow Django ORM patterns