import pytest
from rest_framework.exceptions import PermissionDenied
from rest_framework.test import APIRequestFactory

from personal_finance.users.api.views import UserViewSet
from personal_finance.users.models import User


class TestUserViewSet:
    @pytest.fixture
    def api_rf(self) -> APIRequestFactory:
        return APIRequestFactory()

    @staticmethod
    def test_get_queryset(user: User, api_rf: APIRequestFactory):
        view = UserViewSet()
        request = api_rf.get("/fake-url/")
        request.user = user

        view.request = request

        assert user in view.get_queryset()

    @staticmethod
    def test_get_queryset_invalid_user_id(api_rf: APIRequestFactory):
        """Test that non-integer user ID raises PermissionDenied."""
        from unittest.mock import Mock

        view = UserViewSet()
        request = api_rf.get("/fake-url/")
        
        # Create a mock user with non-integer ID
        mock_user = Mock()
        mock_user.id = "not_an_integer"
        request.user = mock_user

        view.request = request

        with pytest.raises(PermissionDenied, match="User ID must be an integer"):
            view.get_queryset()

    @staticmethod
    def test_me(user: User, api_rf: APIRequestFactory):
        view = UserViewSet()
        request = api_rf.get("/fake-url/")
        request.user = user

        view.request = request

        response = view.me(request)  # type: ignore[call-arg, arg-type, misc]

        assert response.data == {
            "username": user.username,
            "url": f"http://testserver/api/users/{user.username}/",
            "name": user.name,
        }
