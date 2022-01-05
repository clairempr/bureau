from django.test import RequestFactory, TestCase

from bureau.users.tests.factories import UserFactory
from bureau.users.views import UserRedirectView, UserUpdateView


class UserUpdateViewTestCase(TestCase):
    """
    Test UserUpdateView
    """

    def setUp(self):
        self.user = UserFactory()
        self.request_factory = RequestFactory()

    def test_get_success_url(self):
        view = UserUpdateView()
        request = self.request_factory.get("/fake-url/")
        request.user = self.user

        view.request = request

        assert view.get_success_url() == f"/users/{self.user.username}/"

    def test_get_object(self):
        view = UserUpdateView()
        request = self.request_factory.get("/fake-url/")
        request.user = self.user

        view.request = request

        assert view.get_object() == self.user


class UserRedirectViewTestCase(TestCase):
    """
    Test UserRedirectView
    """

    def test_get_redirect_url(self):
        user = UserFactory()
        request_factory = RequestFactory()

        view = UserRedirectView()
        request = request_factory.get("/fake-url")
        request.user = user

        view.request = request

        assert view.get_redirect_url() == f"/users/{user.username}/"
