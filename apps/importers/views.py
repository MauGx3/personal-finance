from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .base import StatementError
from .forms import ImportForm
from .models import ImportBatch
from .services import import_statement, undo_import


@login_required
def import_view(request):
    form = ImportForm(request.POST or None, request.FILES or None, user=request.user)
    outcome = None
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        try:
            outcome = import_statement(
                data["portfolio"],
                data["file"],
                data["file"].name,
                data["parser"] or None,
                data["dry_run"],
            )
        except StatementError as exc:
            form.add_error("file", str(exc))
    context = {
        "form": form,
        "outcome": outcome,
        "batches": ImportBatch.objects.filter(portfolio__user=request.user).select_related(
            "portfolio"
        )[:20],
    }
    return render(request, "importers/import.html", context)


@login_required
@require_POST
def undo_view(request, pk: int):
    batch = get_object_or_404(ImportBatch, pk=pk, portfolio__user=request.user)
    deleted = undo_import(batch)
    messages.success(request, f"Import undone: {deleted} transactions removed.")
    return redirect("importers:import")
