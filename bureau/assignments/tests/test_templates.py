from django.template.loader import render_to_string
from django.test import TestCase

from assignments.tests.factories import AssignmentFactory
from personnel.tests.factories import EmployeeFactory
from places.tests.factories import CityFactory, CountryFactory, PlaceFactory, RegionFactory


class AssignmentListViewTemplateTestCase(TestCase):
    """
    Test template of assignments.views.AssignmentListView
    """

    def setUp(self):
        self.template = 'assignments/assignment_list.html'

    def test_template(self):
        # Specify place name, so there are no issues with names that contain an ampersand
        place = PlaceFactory(city=CityFactory(name='Selma',
                                              region=RegionFactory(name='Alabama'),
                                              country=CountryFactory(name='United States')))

        assignment = AssignmentFactory(employee=EmployeeFactory())

        context = {'place': place, 'assignment_list': {assignment}}
        rendered = render_to_string(self.template, context)

        # "Assignments in <Place>" should be in html
        text = f'Assignments in {place}'
        self.assertTrue(text in rendered, f"'{text}' should be in {self.template}")

        # Assignments should be listed
        self.assertTrue(str(assignment) in rendered, f'Assignments should be listed in {self.template}')
        self.assertTrue(str(assignment.employee) in rendered,
                        f'Assignment employees should be listed in {self.template}')
