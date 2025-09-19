# Code Style and Conventions

## General Style
- **Line length**: 79 characters (configured in pyproject.toml)
- **Python version**: 3.10+ 
- **Type hints**: Used throughout the codebase
- **Docstrings**: Google-style docstrings for classes and methods

## Naming Conventions
- **Classes**: PascalCase (e.g., `BaseStrategy`, `DataSourceBase`)
- **Methods/Functions**: snake_case (e.g., `generate_signals`, `get_current_price`)
- **Variables**: snake_case
- **Constants**: UPPER_SNAKE_CASE
- **Private methods**: Leading underscore (e.g., `_record_failure`)

## Design Patterns
- **Abstract Base Classes**: Used extensively for strategy and data source interfaces
- **Circuit Breaker Pattern**: Implemented in data sources for reliability
- **Factory Pattern**: Strategy registry for creating strategy instances
- **Django ORM**: For database operations and model definitions

## Import Organization
- Standard library imports first
- Third-party imports second
- Local application imports last
- Django imports after third-party

## Error Handling
- Custom exception classes (e.g., `DataSourceError`, `APIError`)
- Proper logging with appropriate levels
- Graceful degradation with fallback mechanisms