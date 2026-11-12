"""Portfolio and transaction pages."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import PortfolioForm, TransactionForm
from .models import Portfolio, Transaction, TransactionKind


class PortfolioCreateView(LoginRequiredMixin, CreateView):
    form_class = PortfolioForm
    template_name = "portfolios/portfolio_form.html"
    success_url = reverse_lazy("core:dashboard")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TransactionListView(LoginRequiredMixin, ListView):
    template_name = "portfolios/transaction_list.html"
    paginate_by = 50

    def get_queryset(self):
        queryset = Transaction.objects.filter(portfolio__user=self.request.user).select_related(
            "asset", "portfolio"
        )
        params = self.request.GET
        if params.get("portfolio", "").isdigit():
            queryset = queryset.filter(portfolio_id=params["portfolio"])
        if params.get("kind") in TransactionKind.values:
            queryset = queryset.filter(kind=params["kind"])
        if params.get("q"):
            queryset = queryset.filter(asset__ticker__icontains=params["q"].strip())
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["portfolios"] = Portfolio.objects.filter(user=self.request.user)
        context["kinds"] = TransactionKind.choices
        query = self.request.GET.copy()
        query.pop("page", None)
        context["querystring"] = query.urlencode()
        return context


class TransactionFormMixin(LoginRequiredMixin):
    form_class = TransactionForm
    template_name = "portfolios/transaction_form.html"
    success_url = reverse_lazy("portfolios:transactions")

    def get_queryset(self):
        return Transaction.objects.filter(portfolio__user=self.request.user)

    def get_form_kwargs(self):
        return {**super().get_form_kwargs(), "user": self.request.user}

    def form_valid(self, form):
        messages.success(self.request, "Transaction saved.")
        return super().form_valid(form)


class TransactionCreateView(TransactionFormMixin, CreateView):
    def get_initial(self):
        return {"portfolio": Portfolio.default_for(self.request.user)}


class TransactionUpdateView(TransactionFormMixin, UpdateView):
    pass


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "portfolios/transaction_confirm_delete.html"
    success_url = reverse_lazy("portfolios:transactions")

    def get_queryset(self):
        return Transaction.objects.filter(portfolio__user=self.request.user)
