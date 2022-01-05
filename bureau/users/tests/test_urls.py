from django.test import TestCase
from django.urls import reverse, resolve

from bureau.users.tests.factories import UserFactory


class UserUrlsTestCase(TestCase):
    """
    Test User urls
    """

    def test_detail(self):
        user = UserFactory()
        assert (
            reverse("users:detail", kwargs={"username": user.username})
            == f"/users/{user.username}/"
        )
        assert resolve(f"/users/{user.username}/").view_name == "users:detail"

    def test_list(self):
        assert reverse("users:list") == "/users/"
        assert resolve("/users/").view_name == "users:list"

    def test_update(self):
        assert reverse("users:update") == "/users/~update/"
        assert resolve("/users/~update/").view_name == "users:update"

    def test_redirect(self):
        assert reverse("users:redirect") == "/users/~redirect/"
        assert resolve("/users/~redirect/").view_name == "users:redirect"
