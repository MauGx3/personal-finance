# [TASK005] - Complete DataProfiler services & validators

**Status:** Pending
**Added:** 2025-09-27
**Updated:** 2025-09-27

## Overview

Replace placeholder `pass` statements in `personal_finance/data_profiler/services.py` and `personal_finance/data_profiler/validators.py` with a complete, well-tested validation flow that converts input data into a sanitized DataFrame and runs DataProfiler analysis. This feature improves data quality and safety when users ingest CSV/JSON files or pass in-memory structures.

## Scope

Included:

- Implement input normalization (pandas/polars DataFrame support) and strict validation of types, missing values, and PII detection using DataProfiler.
- Return a lightweight report (JSON/dict) summarizing detected schema, PII, and suggested corrections.
- Add unit tests for different input shapes: list[dict], pandas.DataFrame, file path, numpy arrays.

Excluded:

- Heavyweight profiling UIs and long-running profiling for huge datasets (these can be added later as async jobs).

## Technical Requirements

- Use `DataProfiler` library if present (prefer lazy usage with local fallback mocks for tests).
- Validators should raise clear, typed exceptions for invalid inputs and never leak sensitive values in exceptions or logs.
- Provide a function `profile_data(data, **options) -> dict` that callers can use programmatically.

## Implementation Plan

1. Implement normalization helpers in `validators.py` to coerce input into a pandas DataFrame and validate shapes/types.
2. Implement `profile_data` in `services.py` which calls DataProfiler and converts the result to a safe JSON-serializable structure.
3. Add tests under `personal_finance/data_profiler/tests/` covering valid inputs, invalid inputs, and PII detection.
4. Add a small CLI or management command example showing `python -m personal_finance.data_profiler.services --path tests/fixtures/sample.csv`.

## Acceptance Criteria

- `profile_data` returns a dict with keys: `rows`, `columns`, `pii_detected` (bool), `fields` (per-column summaries).
- Validators raise `ValueError` with non-sensitive messages for invalid inputs.
- Unit tests pass without requiring external resources.

## Priority

Priority: Medium — improves data safety and onboarding for imports.

## Dependencies

- **Blocked by:** none
- **Blocks:** any feature that relies on automated data quality checks (import pipelines)

## Implementation Size

- Estimated effort: Small/Medium (2-3 days)
- Sub-issues:
  - Normalizers and validators
  - service implementation
  - tests and CLI example
