# Dependency Management Notes

## Dependency File Structure (Updated: Issue #101)

This project uses a structured approach to dependency management with different files serving specific purposes:

### File Purposes

| File | Purpose | Version Format | Usage |
|------|---------|----------------|-------|
| `pyproject.toml` | Package metadata & core dependencies | `>=` constraints | `pip install -e .` |
| `requirements/base.txt` | Production dependencies | `==` pins | Core runtime |
| `requirements/production.txt` | Production-only additions | `==` pins | `-r requirements/production.txt` |
| `requirements/local.txt` | Development dependencies | `==` pins | `-r requirements/local.txt` |
| `constraints.txt` | Version resolution speedup | `==` pins | `-c constraints.txt` |
| `requirements.lock` | Reproducible builds | `==` pins | CI/production deploys |
| `requirements.txt` | CI/CD simplified | `-r` includes | Automated deployments |

### Installation Commands

```bash
# Local development (recommended)
pip install -r requirements/local.txt

# Production deployment
pip install -r requirements/production.txt

# CI/CD with constraints for speed
pip install -r requirements.txt -c constraints.txt

# Package installation
pip install -e .

# Reproducible build
pip install -r requirements.lock
```

### Dependency Consistency Rules

1. **Core dependencies** in `pyproject.toml` use minimum version constraints (`>=`)
2. **All requirements/*.txt files** use exact pins (`==`) for reproducibility
3. **constraints.txt** provides speed optimization with compatible versions
4. **requirements.lock** captures exact versions for reproducible deployments

### Updating Dependencies

1. Update version in `constraints.txt` first
2. Update corresponding requirements files
3. Test with `pip install -r requirements/local.txt`
4. Regenerate `requirements.lock`:
   ```bash
   python -m venv .venv
   .venv/bin/python -m pip install -r requirements.txt -c constraints.txt
   .venv/bin/python -m pip freeze > requirements.lock
   ```
5. Run tests: `pytest tests/test_dependency_consistency.py`

## rcssmin & django-compressor Compatibility

### Issue Resolution (Issue #86)
**Problem**: Dependency conflict when attempting to upgrade `rcssmin` from `1.1.2` to `1.2.1`.

**Error**: 
```
ERROR: Cannot install django-compressor==4.5.1 and rcssmin==1.2.1 because these package versions have conflicting dependencies.
```

**Resolution**: Maintained stable configuration with `rcssmin==1.1.2` and `django-compressor==4.5.1`.

### Why This Decision Was Made
1. **Production Stability**: CSS compression is critical for production performance
2. **Hard Dependency**: `django-compressor==4.5.1` (latest) explicitly requires `rcssmin==1.1.2`
3. **Low Security Risk**: CSS minifiers have minimal security implications
4. **Active Maintenance**: Both packages are actively maintained

### Future Upgrade Path
- Monitor `django-compressor` releases for newer `rcssmin` support
- Consider alternative CSS minification if needed
- Upgrade when dependency constraints are relaxed

### Testing
Run `pytest tests/test_dependency_compatibility.py` to verify CSS compression functionality.

---
*Last Updated: December 2024*
*Related Issues: #86, #101*