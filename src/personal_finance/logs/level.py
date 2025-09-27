"""Logging level utilities and shared constants.

This module centralizes allowed log levels, the default level, a
resolver that validates PORTFOLIO_LOG_LEVEL and a shared log format
used by the package loggers.

Security: validating the log level prevents accidental enabling of
debug-level logging when an invalid/malformed environment variable is set.
"""

from __future__ import annotations

from typing import Iterable


ALLOWED_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})
DEFAULT_LEVEL = "INFO"

# Shared format used by package loggers
LOG_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss,SSS} - {extra[name]} - {level} - {message}"
)


def resolve_level(value: str | None) -> str:
    """Resolve and validate a log level string.

    - Upper-cases the input.
    - Returns DEFAULT_LEVEL when the input is None or not in ALLOWED_LEVELS.
    """
    if not value:
        return DEFAULT_LEVEL

    normalized = value.upper()
    if normalized in ALLOWED_LEVELS:
        return normalized
    return DEFAULT_LEVEL


def allowed_levels() -> Iterable[str]:
    return sorted(ALLOWED_LEVELS)
