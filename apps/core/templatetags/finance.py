"""Template helpers for money, quantities and the value chart."""

from __future__ import annotations

import json
from decimal import Decimal

from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from apps.core.money import quantize_money

register = template.Library()

_SYMBOLS = {"BRL": "R$", "USD": "US$", "EUR": "€"}


def _grouped(value: Decimal, places: int = 2) -> str:
    """Format with Brazilian separators: 1.234,56."""
    text = f"{value:,.{places}f}"
    return text.replace(",", " ").replace(".", ",").replace(" ", ".")


@register.filter
def money(value, currency: str = "") -> str:
    if value is None or value == "":
        return "–"
    amount = _grouped(quantize_money(Decimal(value)))
    symbol = _SYMBOLS.get(currency, currency)
    return f"{symbol} {amount}" if symbol else amount


@register.filter
def signed_money(value, currency: str = "") -> str:
    if value is None or value == "":
        return "–"
    value = Decimal(value)
    sign = "+" if value > 0 else "−" if value < 0 else ""
    return f"{sign}{money(abs(value), currency)}"


@register.filter
def quantity(value) -> str:
    if value is None or value == "":
        return "–"
    value = Decimal(value).normalize()
    places = max(0, -value.as_tuple().exponent)
    return _grouped(value, min(places, 8))


@register.filter
def percent(value) -> str:
    if value is None or value == "":
        return "–"
    value = Decimal(value)
    sign = "+" if value > 0 else "−" if value < 0 else ""
    return f"{sign}{_grouped(abs(value), 1)}%"


@register.filter
def share(value) -> str:
    """An unsigned percentage, for weights."""
    return "–" if value is None else f"{_grouped(Decimal(value), 1)}%"


@register.filter
def tone(value) -> str:
    """CSS class for a gain or loss. The sign in the text carries the meaning too."""
    if value is None or value == "":
        return ""
    return "up" if Decimal(value) > 0 else "down" if Decimal(value) < 0 else ""


@register.simple_tag
def line_chart(points, currency: str = "", width: int = 760, height: int = 240) -> str:
    """Render ``[(date, value), ...]`` as a single-series SVG line chart."""
    points = [(day, Decimal(value)) for day, value in points]
    if len(points) < 2:
        return mark_safe('<p class="empty">Not enough history to draw a chart yet.</p>')

    left, right, top, bottom = 8, 8, 12, 24
    low = min(value for _, value in points)
    high = max(value for _, value in points)
    low = Decimal(0) if low >= 0 and low < high / 2 else low
    span = (high - low) or Decimal(1)
    plot_w, plot_h = width - left - right, height - top - bottom

    def x(index: int) -> float:
        return left + plot_w * index / (len(points) - 1)

    def y(value: Decimal) -> float:
        return top + plot_h * float(1 - (value - low) / span)

    path = " ".join(
        f"{'M' if i == 0 else 'L'}{x(i):.1f},{y(value):.1f}" for i, (_, value) in enumerate(points)
    )
    grid = "".join(
        f'<line class="grid" x1="{left}" x2="{width - right}" y1="{y(level):.1f}" y2="{y(level):.1f}"/>'
        f'<text class="tick" x="{left}" y="{y(level) - 4:.1f}">{money(level, currency)}</text>'
        for level in (low + span * Decimal(step) / 2 for step in (0, 1, 2))
    )
    data = json.dumps(
        [
            {
                "x": round(x(i), 1),
                "y": round(y(v), 1),
                "d": d.strftime("%d/%m/%Y"),
                "v": money(v, currency),
            }
            for i, (d, v) in enumerate(points)
        ]
    )
    return format_html(
        '<figure class="chart" data-points="{}">'
        '<svg viewBox="0 0 {} {}" role="img" aria-label="Portfolio value from {} to {}">'
        "{}"
        '<path class="line" d="{}"/>'
        '<line class="cursor" y1="{}" y2="{}" hidden/><circle class="dot" r="4" hidden/>'
        '<text class="tick" x="{}" y="{}">{}</text>'
        '<text class="tick end" x="{}" y="{}">{}</text>'
        '</svg><div class="tooltip" hidden></div></figure>',
        data, width, height,
        points[0][0].strftime("%d/%m/%Y"), points[-1][0].strftime("%d/%m/%Y"),
        mark_safe(grid), path, top, top + plot_h,
        left, height - 6, points[0][0].strftime("%b %Y"),
        width - right, height - 6, points[-1][0].strftime("%b %Y"),
    )  # fmt: skip
