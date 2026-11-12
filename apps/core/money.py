"""Decimal helpers shared by every app.

Money never touches ``float`` in this project. These helpers are the single
place where outside values (spreadsheet cells, provider payloads, Brazilian
formatted strings) are turned into :class:`~decimal.Decimal`.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

ZERO = Decimal("0")
CENT = Decimal("0.01")

_NUMERIC_JUNK = re.compile(r"[^\d,.\-]")
_DATE_FORMATS = ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y", "%d.%m.%Y")


def to_decimal(value: object) -> Decimal:
    """Convert ``value`` to ``Decimal`` without float artefacts.

    Raises:
        ValueError: if the value is not a finite number.
    """
    if isinstance(value, Decimal):
        result = value
    elif isinstance(value, bool):
        raise ValueError(f"Not a number: {value!r}")
    else:
        try:
            result = Decimal(str(value).strip())
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(f"Not a number: {value!r}") from exc
    if not result.is_finite():
        raise ValueError(f"Not a finite number: {value!r}")
    return result


def quantize_money(value: Decimal) -> Decimal:
    """Round to cents, half up (the convention on Brazilian statements)."""
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def _decimal_mark(text: str) -> str:
    """Which separator in ``text`` is the decimal mark: ``","``, ``"."`` or ``""`` (none)."""
    last_comma, last_dot = text.rfind(","), text.rfind(".")
    if last_comma >= 0 and last_dot >= 0:
        return "," if last_comma > last_dot else "."
    if last_comma >= 0:
        return ","
    if last_dot < 0:
        return ""
    # A lone dot followed by exactly three digits reads as a thousands separator.
    is_thousands = text.count(".") > 1 or len(text) - last_dot - 1 == 3
    return "" if is_thousands else "."


def parse_decimal(value: object) -> Decimal:
    """Parse a number that may be formatted the Brazilian or the US way.

    Accepts real numbers (as produced by spreadsheet readers) and strings such
    as ``"R$ 1.234,56"``, ``"1,234.56"``, ``"(123,45)"`` and ``"-"``.
    The last separator in the string is taken as the decimal mark, so both
    conventions parse correctly; a lone separator followed by exactly three
    digits (``"1.234"``) is ambiguous and is read the Brazilian way, as a
    thousands separator.

    Raises:
        ValueError: if nothing numeric can be read.
    """
    if isinstance(value, int | float | Decimal) and not isinstance(value, bool):
        return to_decimal(value)

    text = str(value or "").strip()
    if text in {"", "-"}:
        return ZERO
    negative = text.startswith("(") and text.endswith(")")
    text = _NUMERIC_JUNK.sub("", text)
    if text.startswith("-"):
        negative = True
    text = text.replace("-", "")
    if not text:
        raise ValueError(f"Not a number: {value!r}")

    decimal_mark = _decimal_mark(text)
    if decimal_mark:
        whole, _, fraction = text.rpartition(decimal_mark)
        text = re.sub(r"[.,]", "", whole) + "." + fraction
    else:
        text = re.sub(r"[.,]", "", text)

    number = to_decimal(text)
    return -number if negative else number


def parse_date(value: object) -> date:
    """Parse a date cell: a real date, or text in day-first / ISO format.

    Raises:
        ValueError: if the value is not a recognisable date.
    """
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value or "").strip()[:10]
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Not a date: {value!r}")
