from django.template.loader import render_to_string
from django.test import TestCase
from django.urls import reverse

class StatisticsTemplateTestCase(TestCase):
    """
    Test template of personnel.Views.StatisticsView
    """

    def setUp(self):
        self.template = 'personnel/statistics.html'

    def test_statistics_template(self):
        context = {'employee_count': 1,
                   'colored_count': 2,
                   'confederate_count': 3,
                   'female_count': 4,
                   'vrc_count': 5,}

        rendered = render_to_string(self.template, context)
        self.assertInHTML('<title>Statistics</title>', rendered)
