from django.test import RequestFactory, TestCase
from django.urls import reverse

from military.tests.factories import RegimentFactory
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

    def test_get_queryset(self):
        """
        If GET parameter 'search_text' is supplied, get_queryset() should filter the default queryset (all Regiments)
        """

        maine_regt = RegimentFactory(name='3rd Maine Infantry')
        usct_regt = RegimentFactory(name='113th US Colored Infantry')
        vrc_regt = RegimentFactory(name='24th Regiment, Veteran Reserve Corps')

        # If no GET parameter 'search_text' supplied, get_queryset() should return default queryset (all Regiments)
        request = RequestFactory().get('/')
        view = RegimentListView(kwargs={}, object_list=[], request=request)
        queryset = view.get_queryset()
        self.assertSetEqual(set(queryset), {maine_regt, usct_regt, vrc_regt},
                            "RegimentListView.get_queryset() should return all regiments if no 'search_text' supplied")

        # If 'search_text' parameter supplied, get_queryset() should filter the default queryset
        request = RequestFactory().get('/', {'search_text': 'Maine'})
        view = RegimentListView(kwargs={}, object_list=[], request=request)
        queryset = view.get_queryset()
        self.assertIn(maine_regt, queryset,
                      "RegimentListView.get_queryset() should return regiments whose names contain 'search_text'")
        for regiment in [usct_regt, vrc_regt]:
            self.assertNotIn(regiment, queryset,
                      "RegimentListView.get_queryset() should return only regiments whose names contain 'search_text'")
