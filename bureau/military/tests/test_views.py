from django.test import RequestFactory, TestCase
from django.urls import reverse

from military.views import RegimentListView

class RegimentListViewTestCase(TestCase):
    """
    Test RegimentListView
    """

    def setUp(self):
        self.url = 'military:regiment_list'

    def test_get_context_data(self):
        """
        context should contain RegimentListView's regiment_type, set to True
        If GET parameter 'search_text' was supplied, that should also be in context
        """

        # context[regiment_type] should be True
        request = RequestFactory().get('/')
        view = RegimentListView(regiment_type='some_regiments', kwargs={}, object_list=[], request=request)
        context = view.get_context_data()
        self.assertTrue(context[view.regiment_type], 'RegimentListView.regiment_type should be True in context')

        # If GET parameter search_text was supplied, that should be in context
        search_text = 'this is the search text'
        response = self.client.get(reverse(self.url), {'search_text': search_text})
        self.assertEqual(response.context['search_text'], search_text,
                         "If 'search_text' was supplied, it should be in context of RegimentListView")

        # If GET parameter search_text not supplied, context['search_text'] should be empty
        response = self.client.get(reverse(self.url))
        self.assertEqual(response.context['search_text'], '',
                         "If 'search_text' wasn't supplied, it should be empty in context of RegimentListView")
