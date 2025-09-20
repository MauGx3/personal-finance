# Code Style and Conventions

## Code Style
- **Line Length**: 79 characters (enforced by ruff)
- **Python Version**: 3.13+
- **Formatter**: Ruff 
- **Linter**: Ruff with extended rules

## Naming Conventions
- **Files**: snake_case
- **Classes**: PascalCase 
- **Functions/Variables**: snake_case
- **Constants**: UPPER_SNAKE_CASE
- **Private members**: Leading underscore (_private)

## Django Conventions
- **Models**: Singular names (User, Portfolio, Asset)
- **Apps**: Plural names (assets, portfolios, users)
- **Views**: Descriptive action names
- **URLs**: RESTful patterns with namespaces

## Test Conventions
- **Test files**: `test_<component>_<type>.py`
- **Test classes**: `Test<Feature><TestType>`
- **Test methods**: `test_<functionality>_<scenario>`

## Documentation
- **Docstrings**: Google style for classes and functions
- **Type hints**: Required for public APIs
- **Comments**: Explain WHY, not WHAT

## Financial Code Guidelines
- Use Decimal for monetary calculations (avoid float)
- Validate financial formulas with known test cases
- Include unit tests for all financial calculations
- Document formula sources and assumptions

## Migration Strategy
- Test incrementally when adding new apps
- Ensure migrations exist before enabling test coverage
- Use graceful imports for optional dependencies
- Keep CI/CD stable with minimal working tests