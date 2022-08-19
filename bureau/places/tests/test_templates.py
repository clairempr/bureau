from django.template.loader import render_to_string
from django.test import TestCase

from personnel.tests.factories import EmployeeFactory
from places.tests.factories import CityFactory, PlaceFactory, BureauStateFactory


class BureauStateDetailViewTemplateTestCase(TestCase):
    """
    Test template of places.views.BureauStateDetailView
    """

    def setUp(self):
        self.template = 'places/bureau_state_detail.html'
        self.state = BureauStateFactory(name='Pelican State')

    def test_template(self):
        page_header = '<div class="page-header">{state} - {employee_count} {employees}</div>'

        # If no employees/stats/assignment places, employee count should be 0 and there should be
        # "No statistics for this location" and "No assignments found"
        context = {'object': self.state}
        rendered = render_to_string(self.template, context)
        expected_page_header = page_header.format(state=self.state, employee_count=0, employees='employees')
        self.assertInHTML(expected_page_header, rendered)
        for text in ['No statistics for this location', 'No assignments found']:
            self.assertTrue(text in rendered,
                "If no employees/assignments, BureauStateDetailView template should contain '{}'".format(text))

        # One employee: employee count should be "1 employee"
        employee1 = EmployeeFactory(last_name='Butts', first_name='Simeon')
        employee1.bureau_states.add(self.state)
        context = {'object': self.state}
        rendered = render_to_string(self.template, context)
        expected_page_header = page_header.format(state=self.state, employee_count=1, employees='employee')
        self.assertInHTML(expected_page_header, rendered)

        # Two employees: employee count should be "2 employees"
        employee2 = EmployeeFactory(last_name='Bishop', first_name='William')
        employee2.bureau_states.add(self.state)
        rendered = render_to_string(self.template, context)
        expected_page_header = page_header.format(state=self.state, employee_count=2, employees='employees')
        self.assertInHTML(expected_page_header, rendered)

        # Stats/assignment places: should be in html
        assignment_place = PlaceFactory(city=CityFactory(name='Vernon', region=self.state))
        context = {'object': self.state,
                   'stats': [('% VRC', '50.0')],
                   'assignment_places': {assignment_place}}
        rendered = render_to_string(self.template, context)
        self.assertTrue('% VRC' in rendered,
                        'If stats in context, they should be shown in BureauStateDetailView template')
        self.assertTrue(str(assignment_place) in rendered,
                        'If assignment places in context, they should be shown in BureauStateDetailView template')
