import pytest
from django.urls import reverse

from apps.portfolios.models import Holding, Portfolio, Transaction
from tests.conftest import TEST_PASSWORD
from tests.test_importers import NEGOCIACAO, xlsx

pytestmark = pytest.mark.django_db


@pytest.fixture
def web(client, user):
    client.force_login(user)
    return client


@pytest.mark.parametrize(
    "name", ["core:dashboard", "portfolios:transactions", "importers:import", "analytics:reports"]
)
def test_pages_require_login(client, name):
    response = client.get(reverse(name))
    assert response.status_code == 302
    assert response.url.startswith("/login/")


def test_health_is_public(client):
    assert client.get("/healthz/").json() == {"status": "ok"}


def test_login_page_and_sign_in(client, user):
    assert client.get("/login/").status_code == 200
    response = client.post("/login/", {"username": "me@example.com", "password": TEST_PASSWORD})
    assert response.status_code == 302 and response.url == "/"


def test_empty_dashboard_points_to_import(web):
    response = web.get("/")
    assert response.status_code == 200
    assert b"Import a statement" in response.content


def test_dashboard_shows_positions_and_flags_gaps(web, portfolio, petr4, aapl, trade):
    trade(petr4, "BUY", "2024-01-10", 100, 20)
    trade(aapl, "SELL", "2024-01-10", 1, 20)
    response = web.get("/")
    content = response.content.decode()
    assert "PETR4" in content and "R$\xa02.000,00" in content
    assert "Some figures are incomplete" in content and "exceeds" in content
    assert "<svg" in content
    assert web.get(f"/?portfolio={portfolio.pk}").status_code == 200


def test_other_users_portfolio_is_not_reachable(web, other_user):
    theirs = Portfolio.objects.create(user=other_user, name="Theirs")
    assert web.get(f"/?portfolio={theirs.pk}").status_code == 404


def test_create_edit_and_delete_transaction(web, portfolio):
    data = {
        "portfolio": portfolio.pk, "kind": "BUY", "trade_date": "2024-01-10", "ticker": "petr4",
        "exchange": "B3", "quantity": "100", "price": "25.50", "fees": "0", "amount": "0",
    }  # fmt: skip
    assert web.post(reverse("portfolios:transaction-create"), data).status_code == 302
    transaction = Transaction.objects.get()
    assert transaction.asset.ticker == "PETR4"

    data["quantity"] = "150"
    web.post(reverse("portfolios:transaction-update", args=[transaction.pk]), data)
    assert Holding.objects.get().quantity == 150

    listing = web.get(reverse("portfolios:transactions"), {"q": "petr", "kind": "BUY"})
    assert b"PETR4" in listing.content

    web.post(reverse("portfolios:transaction-delete", args=[transaction.pk]))
    assert not Transaction.objects.exists()


def test_transaction_form_rejects_bad_input(web, portfolio, other_user):
    theirs = Portfolio.objects.create(user=other_user, name="Theirs")
    data = {
        "portfolio": theirs.pk, "kind": "BUY", "trade_date": "2024-01-10", "ticker": "bad ticker!",
        "exchange": "B3", "quantity": "0", "price": "1", "fees": "0", "amount": "0",
    }  # fmt: skip
    response = web.post(reverse("portfolios:transaction-create"), data)
    assert response.status_code == 200
    assert set(response.context["form"].errors) >= {"portfolio", "ticker"}
    assert not Transaction.objects.exists()


def test_import_page_upload_and_undo(web, portfolio):
    upload = xlsx(NEGOCIACAO)
    upload.name = "negociacao.xlsx"
    response = web.post(reverse("importers:import"), {"portfolio": portfolio.pk, "file": upload})
    assert response.status_code == 200
    assert b"created 5 transactions" in response.content
    batch = portfolio.import_batches.get()
    assert web.post(reverse("importers:undo", args=[batch.pk])).status_code == 302
    assert not Transaction.objects.exists()


def test_import_page_reports_unreadable_file(web, portfolio):
    from django.core.files.uploadedfile import SimpleUploadedFile

    upload = SimpleUploadedFile("nota.pdf", b"%PDF-1.4")
    response = web.post(reverse("importers:import"), {"portfolio": portfolio.pk, "file": upload})
    assert "Unsupported file type" in response.content.decode()


def test_asset_page_and_edit(web, portfolio, petr4, trade):
    trade(petr4, "BUY", "2024-01-10", 100, 20)
    url = reverse("assets:detail", args=[petr4.pk])
    assert b"PETR4.SA" in web.get(url).content
    web.post(url, {"name": "Petrobras PN", "asset_class": "STOCK", "currency": "BRL",
                   "sector": "", "provider_symbol": "", "is_active": "on"})  # fmt: skip
    petr4.refresh_from_db()
    assert petr4.name == "Petrobras PN"


def test_reports_page(web, portfolio, petr4, trade):
    trade(petr4, "BUY", "2024-01-10", 100, 20)
    trade(petr4, "SELL", "2024-03-05", 10, 30)
    content = web.get(reverse("analytics:reports")).content.decode()
    assert "03/2024" in content and "+R$\xa0100,00" in content


def test_sync_prices_button(web, portfolio, petr4, trade):
    trade(petr4, "BUY", "2024-01-10", 100, 20)
    response = web.post(reverse("core:sync-prices"), follow=True)
    assert b"Prices updated" in response.content
    assert petr4.quotes.exists()


@pytest.mark.parametrize(
    ("next_url", "expected"),
    [
        ("/?portfolio=1", "/?portfolio=1"),
        ("https://evil.example/", "/"),
        ("//evil.example/", "/"),
        ("", "/"),
    ],
)
def test_sync_prices_only_redirects_within_the_site(web, next_url, expected):
    response = web.post(reverse("core:sync-prices"), {"next": next_url})
    assert response.status_code == 302
    assert response.url == expected


def test_create_portfolio(web, user):
    web.post(reverse("portfolios:portfolio-create"), {"name": "Retirement", "description": ""})
    assert Portfolio.objects.get(user=user).name == "Retirement"
