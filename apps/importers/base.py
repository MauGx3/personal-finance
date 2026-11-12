"""Building blocks for statement parsers.

A parser turns the rows of one kind of file into ``ParsedRow`` objects. It
knows nothing about the database. To support a new broker, subclass
``StatementParser`` and add its dotted path to ``settings.IMPORT_PARSERS``.
"""

from __future__ import annotations

import unicodedata
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from apps.core.money import ZERO

Row = Sequence[object]


class StatementError(Exception):
    """The file could not be read or matched to a parser."""


def normalize_header(value: object) -> str:
    """Lower-case, strip accents and squeeze spaces: 'Preço  Unitário' -> 'preco unitario'."""
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return " ".join(text.lower().split())


@dataclass
class ParsedRow:
    trade_date: date
    kind: str
    ticker: str
    quantity: Decimal = ZERO
    price: Decimal = ZERO
    amount: Decimal = ZERO
    fees: Decimal = ZERO
    exchange: str = "B3"
    currency: str = ""
    broker: str = ""
    name: str = ""
    notes: str = ""


@dataclass
class ParseResult:
    rows: list[ParsedRow] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class StatementParser(ABC):
    #: Stable identifier, stored on the batch and part of the row fingerprint.
    name: str = ""
    #: Shown in the upload form.
    label: str = ""
    #: Normalized header names that must all be present.
    required_headers: frozenset[str] = frozenset()

    def find_header(self, table: Sequence[Row]) -> int | None:
        """Index of the header row, looking past any title lines at the top."""
        for index, row in enumerate(table[:15]):
            if self.required_headers <= {normalize_header(cell) for cell in row}:
                return index
        return None

    def parse(self, table: Sequence[Row]) -> ParseResult:
        header_index = self.find_header(table)
        if header_index is None:
            raise StatementError(f"This does not look like a {self.label} file.")
        columns = {normalize_header(cell): i for i, cell in enumerate(table[header_index])}
        result = ParseResult()
        for offset, row in enumerate(table[header_index + 1 :], start=header_index + 2):
            if not any(str(cell or "").strip() for cell in row):
                continue

            def cell(header: str, row=row) -> object:
                index = columns.get(header)
                return row[index] if index is not None and index < len(row) else ""

            try:
                parsed = self.parse_row(cell, result)
            except ValueError as exc:
                result.warnings.append(f"Line {offset}: {exc}")
                continue
            if parsed is not None:
                result.rows.append(parsed)
        return result

    @abstractmethod
    def parse_row(self, cell, result: ParseResult) -> ParsedRow | None:
        """Turn one data row into a ``ParsedRow``, or ``None`` to skip it.

        ``cell(header)`` returns the value under a normalized header name.
        Raise ``ValueError`` to report the row as unreadable.
        """
