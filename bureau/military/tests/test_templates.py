from django.template.loader import render_to_string
from django.test import TestCase

from military.tests.factories import RegimentFactory

class RegimentListViewTemplateTestCase(TestCase):
    """
    Test template of military.views.RegimentListView
    """

    def setUp(self):
        self.template = 'military/regiment_list.html'

    def test_template(self):
        search_text = 'Maine'

        regiment = RegimentFactory(name='3rd Maine Infantry')

        context = {'search_text': search_text, 'regiment_list': [regiment]}
        rendered = render_to_string(self.template, context)

        # "Regiments of Bureau Employees" should be in html
        text = 'Regiments of Bureau Employees'
        self.assertTrue(text in rendered, "'{}' should be in {}".format(text, self.template))

        # Search text should be in html
        self.assertTrue(search_text in rendered, "'{}' should be in {}".format(text, self.template))

        # Regiments should be listed
        self.assertTrue(regiment.name in rendered, 'Regiments should be listed in {}'.format(self.template))
