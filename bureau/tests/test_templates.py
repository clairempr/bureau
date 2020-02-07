from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class HomeTemplateTestCase(TestCase):
    """
    Test Home page
    """

    def setUp(self):
        self.url = reverse('home')
        self.template = 'pages/home.html'

    def test_template_content(self):
        # Non-authenticated user should see "Sign Up" and "Sign In" in menu
        response = self.client.get(self.url)
        for text in ['Sign Up', 'Sign In']:
            self.assertContains(response, text,
                                msg_prefix="Non-authenticated user should see '{}' in menu".format(text))

        User.objects.create_user(username='fred', password='secret')
        self.client.login(username='fred', password='secret')
        response = self.client.get(self.url)
        for text in ['My Profile', 'Sign Out']:
            self.assertContains(response, text,
                                msg_prefix="Non-authenticated user should see '{}' in menu".format(text))

    def test_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, self.template)
