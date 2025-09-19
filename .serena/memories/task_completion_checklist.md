# Task Completion Checklist

When completing any development task, follow these steps:

## Code Quality
- [ ] Run linting: `ruff check .`
- [ ] Run formatting: `ruff format .`
- [ ] Fix any linting errors or warnings
- [ ] Ensure code follows project conventions

## Testing
- [ ] Run relevant tests: `pytest`
- [ ] Add tests for new functionality (if applicable)
- [ ] Ensure all tests pass
- [ ] Run security-specific tests if making security changes

## Security Considerations
- [ ] Check for hardcoded secrets or credentials
- [ ] Validate input sanitization
- [ ] Review network binding configurations (avoid 0.0.0.0 in development)
- [ ] Ensure proper access controls

## Documentation
- [ ] Update README.md if needed
- [ ] Update API documentation if endpoints changed
- [ ] Add docstrings for new functions/classes
- [ ] Update configuration examples

## Database
- [ ] Create/run migrations if schema changed: `python manage.py migrate`
- [ ] Test with both PostgreSQL and SQLite fallback
- [ ] Verify data integrity

## Final Verification
- [ ] Test application manually in development
- [ ] Verify changes work with Docker: `just up`
- [ ] Check application health endpoint
- [ ] Ensure no breaking changes for existing functionality

## Git
- [ ] Commit with conventional commit format
- [ ] Use descriptive commit messages
- [ ] Consider squashing related commits