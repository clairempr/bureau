from django.db.models import Count, FloatField
from django.db.models.functions import Cast
from django.template.loader import render_to_string
from django.test import TestCase

from personnel.tests.factories import EmployeeFactory
from places.models import Region
from places.tests.factories import RegionFactory


class StatisticsTemplateTestCase(TestCase):
    """
    Test template of stats.views.GeneralView
    """

    def setUp(self):
        self.template = 'stats/general.html'

    def test_statistics_template(self):
        context = {'employee_count': 1,
                   'colored_count': 2,
                   'confederate_count': 3,
                   'female_count': 4,
                   'vrc_count': 5,}

        rendered = render_to_string(self.template, context)
        self.assertInHTML('<title>Statistics</title>', rendered)


class StateComparisonViewTemplateTestCase(TestCase):
    """
    Test template of stats.views.StateComparisonView
    """

    def setUp(self):
        self.template = 'stats/state_comparison.html'

        self.florida = RegionFactory(name='Florida')
        self.south_carolina = RegionFactory(name='South Carolina')

        self.florida_employee_count = 3
        self.south_carolina_employee_count = 5

        for i in range(self.florida_employee_count):
            employee = EmployeeFactory()
            employee.bureau_states.add(self.florida)

        for i in range(self.south_carolina_employee_count):
            employee = EmployeeFactory()
            employee.bureau_states.add(self.south_carolina)

    def test_template(self):
        # Stats consist of labels and lists of top states for that stat, annotated with values
        total_employees = Region.objects.annotate(
            value=Cast(Count('employee_employed'), FloatField()))

        context = {'stats': [('Employee count', total_employees)]}
        rendered = render_to_string(self.template, context)

        # Title should be in html
        self.assertInHTML('<title>State Comparison</title>', rendered)

        # Stats label should be in html
        self.assertTrue('Employee count' in rendered, 'Stats label should be shown in StateComparisonView template')

        # State names/employee counts should be in html
        for state in [self.florida, self.south_carolina]:
            self.assertTrue(state.name in rendered)

        for employee_count in [self.florida_employee_count, self.south_carolina_employee_count]:
            self.assertTrue(str(employee_count) in rendered)
