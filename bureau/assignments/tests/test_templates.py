from django.template.loader import render_to_string
from django.test import TestCase

from assignments.tests.factories import AssignmentFactory
from personnel.tests.factories import EmployeeFactory
from places.tests.factories import CityFactory, PlaceFactory

class AssignmentListTemplateTestCase(TestCase):
    """
    Test template of assignments.views.AssignmentListView
    """

    def setUp(self):
        self.template = 'assignments/assignment_list.html'

    def test_template(self):
        place = PlaceFactory(city=CityFactory())

        assignment = AssignmentFactory(employee=EmployeeFactory())

        context = {'place': place, 'assignment_list': [assignment]}
        rendered = render_to_string(self.template, context)

        # "Assignments in <Place>" should be in template
        text = 'Assignments in {}'.format(place)
        self.assertTrue(text in rendered, "'{}' should be in {}".format(text, self.template))

        # Assignments should be listed
        self.assertTrue(str(assignment) in rendered, 'Assignments should be listed in {}'.format(self.template))
        self.assertTrue(str(assignment.employee) in rendered,
                        'Assignment employees should be listed in {}'.format(self.template))
