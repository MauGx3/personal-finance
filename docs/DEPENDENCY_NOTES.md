# Dependency Management Notes

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
*Last Updated: September 2024*
*Related Issue: #86*