# Task Completion Workflow

## When a Task is Completed

### 1. Code Quality Checks
```bash
# Format code
ruff format .

# Check linting
ruff check .

# Fix auto-fixable issues
ruff check . --fix
```

### 2. Testing
```bash
# Run minimal core tests (always working)
python -m pytest tests/test_minimal_core.py -v

# Run all active tests (exclude *.disabled)
python -m pytest tests/ -v --ignore-glob="*/*.disabled"

# For new features, add specific tests:
python -m pytest tests/test_<new_feature>.py -v
```

### 3. Database Validation
```bash
# Check for new migrations needed
python manage.py makemigrations --check --dry-run

# Apply any new migrations
python manage.py migrate
```

### 4. Integration Testing
```bash
# Test Django startup
python manage.py check

# Test database connection
python test_simple_setup.py

# Verify imports work
python -c "import personal_finance; print('Import successful')"
```

### 5. Documentation Updates
- Update relevant README files if functionality changed
- Add docstrings for new public APIs
- Update API documentation if endpoints changed

### 6. Git Best Practices
```bash
# Stage changes
git add .

# Commit with conventional commit format
git commit -m "feat(component): description"
# or "fix(component): description"
# or "test(component): description"

# Check status
git status --porcelain
```

## Pre-commit Validation
The project uses pre-commit hooks for:
- Code formatting (ruff)
- Import sorting
- Trailing whitespace removal
- Large file detection

## CI/CD Considerations
- Only commit tests that pass in CI
- Avoid external API dependencies in core tests
- Keep test execution time under 5 minutes
- Use pytest markers for different test categories