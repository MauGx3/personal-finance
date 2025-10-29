"""Assets views."""

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render

from .models import Portfolio

if TYPE_CHECKING:
    pass


@login_required
def portfolio_detail(request: HttpRequest, portfolio_id: int | None = None):
    """Display a user's portfolio with their holdings/assets."""
    # If no portfolio_id provided, get the user's default portfolio
    if portfolio_id:
        portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user, is_active=True)
    else:
        # Get default portfolio or first active portfolio
        portfolio = Portfolio.objects.filter(user=request.user, is_active=True).first()

    # Get all user's portfolios for navigation
    user_portfolios = Portfolio.objects.filter(user=request.user, is_active=True).order_by(
        "-is_default", "name"
    )

    context = {
        "portfolio": portfolio,
        "user_portfolios": user_portfolios,
        "holdings": (
            portfolio.holdings.filter(is_active=True).select_related("asset") if portfolio else []
        ),
    }

    return render(request, "assets/portfolio_detail.html", context)
