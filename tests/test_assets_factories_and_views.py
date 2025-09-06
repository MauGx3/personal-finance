import pytest
from django.urls import reverse
from rest_framework import status

from personal_finance.assets.tests.factories import AssetFactory
from personal_finance.assets.tests.factories import UserFactory


@pytest.mark.django_db
class TestAssetsPage:
    def test_assets_list_view_requires_login(self, client):
        resp = client.get(reverse("assets:list"))
        # AssetsView is LoginRequiredMixin; should redirect to login
        assert resp.status_code in (302, 301)

    def test_add_button_hidden_for_anonymous(self, client):
        # When anonymous, template shouldn't render the Add button
        resp = client.get(reverse("assets:asset_list"))
        assert resp.status_code == status.HTTP_200_OK
        assert b"Add new" not in resp.content

    def test_assets_page_renders_assets_for_user(self, client):
        # Logged-in user can view /assets/
        user = UserFactory()
        client.force_login(user)
        # Create some assets
        AssetFactory.create_batch(3)
        resp = client.get(reverse("assets:list"))
        assert resp.status_code == status.HTTP_200_OK
        # Should render the page title and a table header
        assert b"All Assets" in resp.content
