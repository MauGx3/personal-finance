"""Read an uploaded CSV or Excel file into a plain table (list of rows)."""

from __future__ import annotations

import csv
import io
from typing import BinaryIO

from .base import StatementError


def read_table(file: BinaryIO, filename: str) -> list[list[object]]:
    data = file.read()
    if not data:
        raise StatementError("The file is empty.")
    lowered = filename.lower()
    if lowered.endswith(".xlsx"):
        return _read_xlsx(data)
    if lowered.endswith((".csv", ".txt")):
        return _read_csv(data)
    raise StatementError("Unsupported file type. Upload a .xlsx or .csv file.")


def _read_xlsx(data: bytes) -> list[list[object]]:
    from openpyxl import load_workbook

    try:
        workbook = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    except Exception as exc:  # openpyxl raises several unrelated types
        raise StatementError(f"Could not open the spreadsheet: {exc}") from exc
    sheet = workbook.worksheets[0]
    return [list(row) for row in sheet.iter_rows(values_only=True)]


def _read_csv(data: bytes) -> list[list[object]]:
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            text = data.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    first_line = text.splitlines()[0] if text.strip() else ""
    delimiter = max(";,\t", key=first_line.count)
    return [list(row) for row in csv.reader(io.StringIO(text), delimiter=delimiter)]
