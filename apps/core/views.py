"""Dashboard and health check."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.analytics.reports import value_history
from apps.data_sources.services import sync_all
from apps.portfolios.models import Portfolio
from apps.portfolios.services.valuation import snapshot


def health(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"status": "ok"})


def selected_portfolios(request: HttpRequest) -> tuple[list[Portfolio], Portfolio | None]:
    """The user's portfolios, narrowed to one when ``?portfolio=<id>`` is given."""
    portfolios = list(Portfolio.objects.filter(user=request.user))
    selected_id = request.GET.get("portfolio")
    if selected_id and selected_id.isdigit():
        selected = get_object_or_404(Portfolio, pk=selected_id, user=request.user)
        return [selected], selected
    return portfolios, None


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    portfolios, selected = selected_portfolios(request)
    context = {
        "all_portfolios": Portfolio.objects.filter(user=request.user),
        "selected": selected,
        "snapshot": snapshot(portfolios),
        "history": value_history(portfolios),
    }
    return render(request, "core/dashboard.html", context)


@login_required
@require_POST
def sync_prices(request: HttpRequest) -> HttpResponse:
    report = sync_all()
    if report.errors:
        failed = ", ".join(sorted(report.errors))
        messages.warning(request, f"Prices updated, but these symbols failed: {failed}.")
    else:
        messages.success(request, f"Prices updated ({report.total} daily closes stored).")
    return redirect(request.POST.get("next") or "core:dashboard")
