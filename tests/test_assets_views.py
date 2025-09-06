import os

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from rest_framework import status

from personal_finance.assets.models import Asset

UserModel = get_user_model()
TEST_PASSWORD = os.environ.get("TEST_PASSWORD", "testpass123")


@pytest.mark.django_db
def test_assets_view_requires_login():
    """Test that assets view requires authentication."""
    client = Client()
    url = reverse("assets:list")
    response = client.get(url)
    # Should redirect to login page
    assert response.status_code == status.HTTP_302_FOUND
    assert "/accounts/login/" in response.url


@pytest.mark.django_db
def test_assets_view_authenticated_access():
    """Test that authenticated users can access assets view."""
    # Create a user
    username_field = getattr(UserModel, "USERNAME_FIELD", "username")
    kwargs = {"password": TEST_PASSWORD, "email": "test@example.com"}
    if username_field != "email":
        kwargs[username_field] = "testuser"

    user = UserModel.objects.create_user(**kwargs)

    client = Client()
    client.force_login(user)

    url = reverse("assets:list")
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert "Financial Assets" in response.context["title"]


@pytest.mark.django_db
def test_assets_view_renders_template():
    """Test that assets view uses correct template."""
    # Create a user
    username_field = getattr(UserModel, "USERNAME_FIELD", "username")
    kwargs = {"password": TEST_PASSWORD, "email": "test@example.com"}
    if username_field != "email":
        kwargs[username_field] = "testuser"

    user = UserModel.objects.create_user(**kwargs)

    client = Client()
    client.force_login(user)

    url = reverse("assets:list")
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert "assets/assets.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_assets_page_displays_assets_list():
    """Test that the assets page displays assets from the database."""
    # Create a user
    username_field = getattr(UserModel, "USERNAME_FIELD", "username")
    kwargs = {"password": TEST_PASSWORD, "email": "test@example.com"}
    if username_field != "email":
        kwargs[username_field] = "testuser"

    user = UserModel.objects.create_user(**kwargs)

    # Create test assets
    Asset.objects.create(
        symbol="AAPL",
        name="Apple Inc.",
        asset_type=Asset.ASSET_STOCK,
        currency="USD",
        exchange="NASDAQ",
    )
    Asset.objects.create(
        symbol="BTC",
        name="Bitcoin",
        asset_type=Asset.ASSET_CRYPTO,
        currency="USD",
    )

    client = Client()
    client.force_login(user)

    url = reverse("assets:list")
    response = client.get(url)

    content = response.content.decode("utf-8")

    # Check that assets are displayed
    assert "AAPL" in content
    assert "Apple Inc." in content
    assert "BTC" in content
    assert "Bitcoin" in content
    assert "2 total" in content  # Should show count of assets


@pytest.mark.django_db
def test_assets_page_shows_empty_state():
    """Test that the assets page shows appropriate message when no assets exist."""
    # Create a user
    username_field = getattr(UserModel, "USERNAME_FIELD", "username")
    kwargs = {"password": TEST_PASSWORD, "email": "test@example.com"}
    if username_field != "email":
        kwargs[username_field] = "testuser"

    user = UserModel.objects.create_user(**kwargs)

    client = Client()
    client.force_login(user)

    url = reverse("assets:list")
    response = client.get(url)

    content = response.content.decode("utf-8")

    # Check for empty state message
    assert "No assets found" in content
    assert "0 total" in content


@pytest.mark.django_db
def test_assets_url_name():
    """Test that the assets URL is correctly named."""
    url = reverse("assets:list")
    assert url == "/assets/"
