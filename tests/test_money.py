from datetime import date, datetime
from decimal import Decimal

import pytest

from apps.core.money import parse_date, parse_decimal, quantize_money, to_decimal


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("R$ 1.234,56", "1234.56"),
        ("1.234,56", "1234.56"),
        ("1,234.56", "1234.56"),
        ("25,50", "25.50"),
        ("25.5", "25.5"),
        ("1.000", "1000"),
        ("1.234.567", "1234567"),
        ("(123,45)", "-123.45"),
        ("-R$ 10,00", "-10.00"),
        ("-", "0"),
        ("", "0"),
        (100, "100"),
        (25.5, "25.5"),
        (Decimal("3.10"), "3.10"),
    ],
)
def test_parse_decimal(raw, expected):
    assert parse_decimal(raw) == Decimal(expected)


@pytest.mark.parametrize("raw", ["abc", "R$", True])
def test_parse_decimal_rejects_non_numbers(raw):
    with pytest.raises(ValueError):
        parse_decimal(raw)


def test_to_decimal_avoids_float_artefacts_and_rejects_nan():
    assert to_decimal(0.1) == Decimal("0.1")
    with pytest.raises(ValueError):
        to_decimal(float("nan"))


def test_quantize_money_rounds_half_up():
    assert quantize_money(Decimal("2.675")) == Decimal("2.68")


@pytest.mark.parametrize(
    "raw",
    ["15/03/2024", "2024-03-15", "15-03-2024", date(2024, 3, 15), datetime(2024, 3, 15, 9, 30)],
)
def test_parse_date(raw):
    assert parse_date(raw) == date(2024, 3, 15)


def test_parse_date_rejects_garbage():
    with pytest.raises(ValueError):
        parse_date("soon")
