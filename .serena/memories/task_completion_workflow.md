# Task Completion Workflow

## When Adding New Functionality

1. **Create Migrations First**: Run `python manage.py makemigrations` for any new apps
2. **Test Incrementally**: Add one app at a time with proper migrations
3. **Verify CI**: Ensure each addition doesn't break the CI pipeline
4. **Add Tests**: Create corresponding test files following naming conventions

## When Expanding Test Suite

1. **Check Migration Status**: Ensure target apps have proper database migrations
2. **Test Locally First**: Verify tests pass locally before committing
3. **Use Existing Patterns**: Follow existing test structure and naming
4. **Mock External Dependencies**: Use mock services for external APIs
5. **Start Small**: Begin with basic model tests before complex integration tests

## Code Quality Checks

1. **Linting**: Run `ruff check .` to check code style
2. **Formatting**: Run `ruff format .` to format code
3. **Testing**: Run `pytest tests/` to ensure all tests pass
4. **Coverage**: Check test coverage with `pytest --cov=personal_finance`

## Before Committing

1. **Run Full Test Suite**: `pytest tests/ -v`
2. **Check Linting**: `ruff check . && ruff format .`
3. **Verify Migrations**: `python manage.py showmigrations`
4. **Test CI Compatibility**: Ensure no external API dependencies in basic tests

## Debugging Test Failures

```bash
# Run failed test with detailed output
pytest tests/test_file.py::TestClass::test_method -vv

# Debug with pdb
pytest tests/ --pdb

# Show local variables on failure
pytest tests/ -l
```

## Best Practices

- **Stability over Coverage**: Focus on reliable tests that won't break CI
- **Gradual Expansion**: Add test coverage incrementally as migrations are created
- **Document Changes**: Update README files when adding new test categories
- **Keep Simple**: Avoid complex dependencies until platform is fully migrated
