"""Logging level utilities and shared constants.

This module centralizes allowed log levels, the default level, a
resolver that validates PORTFOLIO_LOG_LEVEL and a shared log format
used by the package loggers.

Security: validating the log level prevents accidental enabling of
debug-level logging when an invalid/malformed environment variable is set.
"""

from __future__ import annotations

from typing import Iterable


ALLOWED_LEVELS = frozenset(
    {"TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
)
DEFAULT_LEVEL = "INFO"

# Shared format used by package loggers
LOG_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss,SSS} - {extra[name]} - {level} - {message}"
)

# JSON-friendly format for containerized environments.
# loguru can serialize JSON when `serialize=True` is used on handlers; the
# constant documents the fields we include in structured logs.
JSON_FIELDS = [
    "time",
    "extra[name]",
    "level",
    "module",
    "function",
    "line",
    "message",
]


def resolve_level(value: str | None) -> str:
    """Resolve and validate a log level string.

    - Upper-cases and strips the input.
    - Returns DEFAULT_LEVEL when the input is None or not in ALLOWED_LEVELS.
        - When the input is invalid, emits a short, non-sensitive warning to
            stderr so callers (and tests) can detect misconfiguration without
            exposing secrets.
    """
    import sys

    if not value:
        return DEFAULT_LEVEL

    normalized = value.strip().upper()
    if normalized in ALLOWED_LEVELS:
        return normalized

    # Concise non-sensitive warning for invalid configuration
    try:
        sys.stderr.write(
            "warning: invalid PORTFOLIO_LOG_LEVEL='"
            + str(value)
            + f"', defaulting to {DEFAULT_LEVEL}\n"
        )
    except OSError:
        # If stderr isn't available, fail silently and return default
        return DEFAULT_LEVEL
    return DEFAULT_LEVEL


def allowed_levels() -> Iterable[str]:
    return sorted(ALLOWED_LEVELS)
