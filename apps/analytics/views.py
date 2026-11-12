from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.core.views import selected_portfolios
from apps.portfolios.models import Portfolio

from .reports import income_by_month, realized_by_month


@login_required
def reports(request):
    portfolios, selected = selected_portfolios(request)
    context = {
        "all_portfolios": Portfolio.objects.filter(user=request.user),
        "selected": selected,
        "realized": realized_by_month(portfolios),
        "income": income_by_month(portfolios),
    }
    return render(request, "analytics/reports.html", context)
