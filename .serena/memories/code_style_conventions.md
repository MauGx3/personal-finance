# Code Style and Conventions

## Python Style Guidelines
- Follow PEP 8 standards
- Use Google Code Style for Python: https://google.github.io/styleguide/pyguide.html
- Target Python 3.11 features
- Line length: 79 characters (configured in pyproject.toml)

## Documentation
- Use Google-style docstrings
- Every module must have a docstring
- Functions must have docstrings following Google Code Style section 3.8.3
- Sphinx-compatible documentation structure

## Type Annotations
- Use meaningful method, variable and parameter names
- Always annotate data types of parameters and return values
- Use recent Python features instead of older code

## Django Conventions
- Follow Django best practices for models, views, serializers
- Use Django's built-in user model through get_user_model()
- Proper model field choices and constraints
- Use Django's testing framework with pytest-django

## Testing Conventions
- Test files: `test_<component>_<type>.py`
- Test classes: `Test<Feature><TestType>`
- Test methods: `test_<functionality>_<scenario>`
- Use factories for test data creation
- Mock external dependencies (APIs, services)
- Test both success and failure scenarios

## Code Organization
- Modular code structure
- Leverage existing libraries before writing custom solutions
- Avoid magic numbers - use named constants
- Use lazy % string logging
- Don't use bare exceptions
- Define specific Exception classes

## Import Organization
1. Standard library imports (re, math, datetime)
2. Related third party imports (numpy, django)
3. Local application/library specific imports
Blank line between each group.

## Financial Code Specific
- For mathematical/scientific functions, add actual formulas as comments/docstrings
- Use proper decimal precision for financial calculations
- Include edge cases and boundary condition tests
