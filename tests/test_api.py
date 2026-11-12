import pytest
from rest_framework.test import APIClient

from apps.data_sources.models import PriceQuote
from apps.portfolios.models import Portfolio, Transaction

pytestmark = pytest.mark.django_db


@pytest.fixture
def api(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


def test_api_requires_authentication():
    assert APIClient().get("/api/portfolios/").status_code in (401, 403)


def test_schema_is_served(api):
    assert api.get("/api/schema/").status_code == 200


def test_portfolio_crud_is_scoped_to_the_user(api, user, other_user):
    Portfolio.objects.create(user=other_user, name="Theirs")
    created = api.post("/api/portfolios/", {"name": "Main"}, format="json")
    assert created.status_code == 201
    listing = api.get("/api/portfolios/").json()
    assert [p["name"] for p in listing["results"]] == ["Main"]
    assert Portfolio.objects.get(name="Main").user == user


def test_transactions_api(api, portfolio, petr4, other_user):
    body = {"portfolio": portfolio.pk, "asset": petr4.pk, "kind": "BUY",
            "trade_date": "2024-01-10", "quantity": "100", "price": "25.50"}  # fmt: skip
    response = api.post("/api/transactions/", body, format="json")
    assert response.status_code == 201, response.json()
    assert response.json()["total"] == "2550.00"
    assert response.json()["currency"] == "BRL"

    bad = api.post("/api/transactions/", {**body, "quantity": "0"}, format="json")
    assert bad.status_code == 400

    theirs = Portfolio.objects.create(user=other_user, name="Theirs")
    forbidden = api.post("/api/transactions/", {**body, "portfolio": theirs.pk}, format="json")
    assert forbidden.status_code == 400
    assert Transaction.objects.count() == 1

    holdings = api.get("/api/holdings/").json()["results"]
    assert holdings[0]["ticker"] == "PETR4" and holdings[0]["cost_basis"] == "2550.00"


def test_valuation_endpoint(api, portfolio, petr4, trade):
    trade(petr4, "BUY", "2024-01-10", 100, 20)
    PriceQuote.objects.create(asset=petr4, day="2024-06-03", close="30")
    data = api.get(f"/api/portfolios/{portfolio.pk}/valuation/").json()
    assert data["total_value"] == "3000.00"
    assert data["unrealized_gain"] == "1000.00"
    assert data["positions"][0]["ticker"] == "PETR4"


def test_assets_api_search_and_no_delete(api, petr4):
    assert api.get("/api/assets/?search=PETR").json()["count"] == 1
    assert api.delete(f"/api/assets/{petr4.pk}/").status_code == 405
