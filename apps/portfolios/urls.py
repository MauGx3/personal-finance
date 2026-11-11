from django.urls import path

from . import views

app_name = "portfolios"

urlpatterns = [
    path("portfolios/new/", views.PortfolioCreateView.as_view(), name="portfolio-create"),
    path("transactions/", views.TransactionListView.as_view(), name="transactions"),
    path("transactions/new/", views.TransactionCreateView.as_view(), name="transaction-create"),
    path(
        "transactions/<int:pk>/", views.TransactionUpdateView.as_view(), name="transaction-update"
    ),
    path(
        "transactions/<int:pk>/delete/",
        views.TransactionDeleteView.as_view(),
        name="transaction-delete",
    ),
]
