"""
Minimal shim for the `loguru` package used in tests.

This file provides a very small, in-repo implementation of the parts of
loguru used by the project so tests can run in the green phase without
installing the real dependency. It intentionally implements a no-frills
logger with the following features:

- a module-level `logger` object
- logger.remove(), logger.add(stream, level, format, colorize)
- logger.bind(**extra) returning a bound logger with same methods
- methods: info, warning, error, debug

This shim is only intended for tests and the TDD green phase. The real
`loguru` package should be used in production.
"""

from __future__ import annotations

import sys
from typing import Any


class _BoundLogger:
    def __init__(
        self, parent: _SimpleLogger, bound_extra: dict[str, Any] | None = None
    ):
        self._parent = parent
        self._extra = dict(bound_extra) if bound_extra else {}

    def _format(self, message: str) -> str:
        # Minimal formatting: include bound name if present
        name = self._extra.get("name")
        if name:
            return f"{name} - {message}"
        return message

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        if args:
            try:
                message = message % args
            except Exception:
                pass
        print(self._format(message), file=sys.stdout)

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        if args:
            try:
                message = message % args
            except Exception:
                pass
        print(self._format(message), file=sys.stdout)

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        if args:
            try:
                message = message % args
            except Exception:
                pass
        print(self._format(message), file=sys.stderr)

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        if args:
            try:
                message = message % args
            except Exception:
                pass
        print(self._format(message), file=sys.stdout)

    def bind(self, **extra: Any) -> _BoundLogger:
        merged = dict(self._extra)
        merged.update(extra)
        return _BoundLogger(self._parent, merged)


class _SimpleLogger:
    def __init__(self) -> None:
        self._handlers = []

    def remove(self) -> None:
        # No-op for shim: clear handlers
        self._handlers.clear()

    def add(
        self,
        stream,
        level: str | None = None,
        format: str | None = None,
        colorize: bool = False,
        **kwargs,
    ) -> int:
        # Record a handler tuple; return a fake handler id
        handler_id = len(self._handlers) + 1
        self._handlers.append(
            (handler_id, stream, level, format, colorize, kwargs)
        )
        return handler_id

    def bind(self, **extra: Any) -> _BoundLogger:
        return _BoundLogger(self, extra)

    # Expose convenience methods on the root logger too
    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.bind().info(message, *args, **kwargs)

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.bind().warning(message, *args, **kwargs)

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.bind().error(message, *args, **kwargs)

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.bind().debug(message, *args, **kwargs)


# Module-level logger instance to mimic `from loguru import logger`
logger = _SimpleLogger()
