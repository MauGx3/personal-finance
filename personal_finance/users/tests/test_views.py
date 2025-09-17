from http import HTTPStatus

import pytest
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.http import HttpResponseRedirect
from django.test import RequestFactory
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from personal_finance.users.forms import UserAdminChangeForm
from personal_finance.users.models import User
from personal_finance.users.tests.factories import UserFactory
from personal_finance.users.views import UserRedirectView
from personal_finance.users.views import UserUpdateView
from personal_finance.users.views import user_detail_view

pytestmark = pytest.mark.django_db


class TestUserUpdateView:
    """
    TODO:
        extracting view initialization code as class-scoped fixture
        would be great if only pytest-django supported non-function-scoped
        fixture db access -- this is a work-in-progress for now:
        https://github.com/pytest-dev/pytest-django/pull/258
    """

    @staticmethod
    def dummy_get_response(request: HttpRequest):
        return None

    @staticmethod
    def test_get_success_url(user: User, rf: RequestFactory):
        view = UserUpdateView()
        request = rf.get("/fake-url/")
        request.user = user

        view.request = request
        assert view.get_success_url() == f"/users/{user.username}/"

    @staticmethod
    def test_get_success_url_unauthenticated_user(rf: RequestFactory):
        view = UserUpdateView()
        request = rf.get("/fake-url/")
        request.user = AnonymousUser()

        view.request = request

        with pytest.raises(
            PermissionDenied, match="User must be authenticated"
        ):
            view.get_success_url()

    @staticmethod
    def test_get_object(user: User, rf: RequestFactory):
        view = UserUpdateView()
        request = rf.get("/fake-url/")
        request.user = user

        view.request = request

        assert view.get_object() == user

    @staticmethod
    def test_get_object_unauthenticated_user(rf: RequestFactory):
        view = UserUpdateView()
        request = rf.get("/fake-url/")
        request.user = AnonymousUser()

        view.request = request

        with pytest.raises(
            PermissionDenied, match="User must be authenticated"
        ):
            view.get_object()

    def test_form_valid(self, user: User, rf: RequestFactory):
        view = UserUpdateView()
        request = rf.get("/fake-url/")

        # Add the session/message middleware to the request
        SessionMiddleware(self.dummy_get_response).process_request(request)
        MessageMiddleware(self.dummy_get_response).process_request(request)
        request.user = user

        view.request = request

        # Initialize the form
        form = UserAdminChangeForm()
        form.cleaned_data = {}
        form.instance = user
        view.form_valid(form)

        messages_sent = [m.message for m in messages.get_messages(request)]
        assert messages_sent == [_("Information successfully updated")]


class TestUserRedirectView:
    @staticmethod
    def test_get_redirect_url(user: User, rf: RequestFactory):
        view = UserRedirectView()
        request = rf.get("/fake-url")
        request.user = user

        view.request = request
        assert view.get_redirect_url() == f"/users/{user.username}/"


class TestUserDetailView:
    @staticmethod
    def test_authenticated(user: User, rf: RequestFactory):
        request = rf.get("/fake-url/")
        request.user = UserFactory()
        response = user_detail_view(request, username=user.username)

        assert response.status_code == HTTPStatus.OK

    @staticmethod
    def test_not_authenticated(user: User, rf: RequestFactory):
        request = rf.get("/fake-url/")
        request.user = AnonymousUser()
        response = user_detail_view(request, username=user.username)
        login_url = reverse(settings.LOGIN_URL)

        assert isinstance(response, HttpResponseRedirect)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == f"{login_url}?next=/fake-url/"
