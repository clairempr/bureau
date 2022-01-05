from django.test import TestCase

from bureau.users.tests.factories import UserFactory


class UserTestCase(TestCase):
    """
    Test User model
    """

    def test_user_get_absolute_url(self):
        user = UserFactory()
        assert user.get_absolute_url() == f"/users/{user.username}/"
