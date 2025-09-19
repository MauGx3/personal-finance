# Task Completion Checklist

When completing a development task, ensure the following:

## Code Quality
- [ ] Run `python -m ruff check .` and fix any linting issues
- [ ] Run `python -m ruff format .` to format code
- [ ] Run `python -m pylint personal_finance/` and address critical issues
- [ ] Verify no abstract method violations (PYL-W0223)

## Testing
- [ ] Run `python -m pytest` to ensure all tests pass
- [ ] Add new tests for any new functionality
- [ ] Verify test coverage for modified code

## Database
- [ ] Run migrations if model changes: `python manage.py migrate`
- [ ] Update migration files if needed: `python manage.py makemigrations`

## Documentation
- [ ] Update docstrings for new/modified methods
- [ ] Update README if public API changes
- [ ] Add type hints for new functions/methods

## Git Workflow
- [ ] Use conventional commits format (feat:, fix:, docs:, etc.)
- [ ] Keep commits atomic and focused
- [ ] No initial capital letter in commit description
- [ ] Commit message under 72 characters

## Final Verification
- [ ] Code follows established patterns and conventions
- [ ] No breaking changes to existing functionality
- [ ] All abstract methods are properly implemented
- [ ] Error handling is appropriate and consistent