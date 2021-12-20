from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from assignments.tests.factories import AssignmentFactory, PositionFactory
from assignments.views import AssignmentListView, BureauHeadquartersAssignmentListView
from personnel.tests.factories import EmployeeFactory
from places.tests.factories import CityFactory, CountyFactory, PlaceFactory, RegionFactory

class AssignmentListViewTestCase(TestCase):
    """
    Test AssignmentListView
    """

    def setUp(self):
        self.place = PlaceFactory()
        self.view = AssignmentListView()

    def test_get_place(self):
        """
        If 'place' is in kwargs and it's the pk of a Place, then Place should be returned,
        otherwise None should be returned
        """

        self.view.kwargs = {}
        self.assertIsNone(self.view.get_place(),
                          "AssignmentListView.get_place() should return None if 'place' not in kwargs")

        self.view.kwargs = {'place': 1}
        self.assertIsNone(self.view.get_place(),
                          "AssignmentListView.get_place() should return None if Place obj not found")

        self.view.kwargs = {'place': self.place.pk}
        self.assertEqual(self.view.get_place(), self.place,
                          "AssignmentListView.get_place() should return Place with pk 'place'")

    @patch.object(AssignmentListView, 'get_place', autospec=True)
    def test_get_context_data(self, mock_get_place):
        """
        get_context_data() should fill 'place' with specified place
        """

        # If no 'place', context['place'] should be empty
        mock_get_place.return_value = None
        response = self.client.get(reverse('assignments:assignment_list'))
        self.assertIsNone(response.context['place'],
                "If place is None, AssignmentListView context['place'] should be None")

        # If 'place' is found, it should go in context['place']
        mock_get_place.return_value = self.place
        response = self.client.get(reverse('assignments:assignment_list', kwargs={'place': self.place.pk}))
        self.assertEqual(response.context['place'], self.place,
                "If place is found, it should go in AssignmentListView context['place']")

    @patch.object(AssignmentListView, 'get_place', autospec=True)
    def test_get_queryset(self, mock_get_place):
        """
        If a place is specified, get_queryset() should only return assignments in that exact place,
        not places in that place

        If no place specified, it should return all assignments
        """

        # Set up places
        tennessee = PlaceFactory(city=None, county=None, region=RegionFactory(name='Tennessee'))
        franklin = PlaceFactory(city=CityFactory(name='Franklin'), region=tennessee.region)
        knox_county = PlaceFactory(city=None, county=CountyFactory(name='Knox County', state=tennessee.region))

        # Set up assignments
        assignment_in_tennessee = AssignmentFactory(employee=EmployeeFactory(
            last_name='Gelray', first_name='Joseph Wiley'))
        assignment_in_tennessee.positions.add(PositionFactory(title='Inspector'))
        assignment_in_tennessee.places.add(tennessee)

        assignment_in_franklin = AssignmentFactory(employee=EmployeeFactory(
            last_name='Judd', first_name='George Edwin'))
        assignment_in_franklin.positions.add(PositionFactory(title='Superintendent'))
        assignment_in_franklin.places.add(franklin)

        assignment_in_knox_county = AssignmentFactory(employee=EmployeeFactory(
            last_name='Walker', first_name='Samuel'))
        assignment_in_knox_county.positions.add(PositionFactory(title='Subassistant Commissioner'))
        assignment_in_knox_county.places.add(knox_county)

        # No place specified, should return default queryset (all assignments)
        mock_get_place.return_value = None
        queryset = self.view.get_queryset()
        for assignment in [assignment_in_tennessee, assignment_in_franklin, assignment_in_knox_county]:
            self.assertIn(assignment, queryset,
                          'AssignmentListView.get_queryset() should return all assignments if no place specified')

        # If Tennessee specified, should return assignment in Tennessee (but not in Franklin or Knox Co., Tennessee)
        mock_get_place.return_value = tennessee
        queryset = self.view.get_queryset()
        self.assertIn(assignment_in_tennessee, queryset,
                      'AssignmentListView.get_queryset() should return assignment in state only if state specified')
        self.assertNotIn(assignment_in_franklin, queryset,
                      "AssignmentListView.get_queryset() shouldn't return assignment in city if state specified")
        self.assertNotIn(assignment_in_knox_county, queryset,
                      "AssignmentListView.get_queryset() shouldn't return assignment in county if state specified")

        # If Franklin, Tennessee specified, should return assignment in Franklin (but not in Knox Co. or Tennessee only)
        mock_get_place.return_value = franklin
        queryset = self.view.get_queryset()
        self.assertIn(assignment_in_franklin, queryset,
                      'AssignmentListView.get_queryset() should return assignment in city only if city specified')
        self.assertNotIn(assignment_in_tennessee, queryset,
                      "AssignmentListView.get_queryset() shouldn't return assignment in state only if city specified")
        self.assertNotIn(assignment_in_knox_county, queryset,
                      "AssignmentListView.get_queryset() shouldn't return assignment in county if city specified")

        # If Knox County, Tennessee specified, should return assignment in Knox Co. (but not in Franklin or Tennessee only)
        mock_get_place.return_value = knox_county
        queryset = self.view.get_queryset()
        self.assertIn(assignment_in_knox_county, queryset,
                      'AssignmentListView.get_queryset() should return assignment in county only if county specified')
        self.assertNotIn(assignment_in_tennessee, queryset,
                      "AssignmentListView.get_queryset() shouldn't return assignment in state only if county specified")
        self.assertNotIn(assignment_in_franklin, queryset,
                      "AssignmentListView.get_queryset() shouldn't return assignment in city if county specified")

class BureauHeadquartersAssignmentListViewTestCase(TestCase):
    """
    Test BureauHeadquartersAssignmentListView
    """

    def test_get_queryset(self):
        """
        get_queryset() should return assignments where bureau_headquarters is set to True
        """

        view = BureauHeadquartersAssignmentListView()

        bureau_headquarters_assignment = AssignmentFactory(bureau_headquarters=True)
        other_assignment = AssignmentFactory(bureau_headquarters=False)

        queryset = view.get_queryset()
        self.assertIn(bureau_headquarters_assignment, queryset,
            'BureauHeadquartersAssignmentListView.get_queryset() should return Bureau Headquarters assignment')
        self.assertNotIn(other_assignment, queryset,
            "BureauHeadquartersAssignmentListView.get_queryset() shouldn't return non-Bureau Headquarters assignment")
