from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from assignments.tests.factories import AssignmentFactory
from medical.tests.factories import AilmentFactory, AilmentTypeFactory
from places.tests.factories import CityFactory, CountyFactory, PlaceFactory, RegionFactory
from places.views import BureauStateDetailView

class BureauStateDetailViewTestCase(TestCase):
    """
    Test BureauStateDetail
    """

    def setUp(self):
        self.state = RegionFactory(name='Old North State')
        self.state_url = reverse('places:bureau_state_detail', kwargs={'pk': self.state.pk})
        self.bureau_headquarters = RegionFactory(bureau_headquarters=True)
        self.bureau_headquarters_url = reverse('places:bureau_state_detail', kwargs={'pk': self.bureau_headquarters.pk})

    def test_get_context_data(self):
        #Test it with no assignments at all
        response = self.client.get(self.state_url)
        for key in ['assignment_places', 'stats']:
            self.assertIn(key, response.context, "'{}' should be in context of BureauStateDetailView".format(key))

        # With no assignments, assignment_places should be empty
        self.assertFalse(response.context['assignment_places'].exists(),
                          'BureauStateDetailView context assignment_places should be empty when no assignments in state')

        # Test returning the right assignment locations in context
        place_in_state = PlaceFactory(region=self.state)
        assignment_in_state = AssignmentFactory()
        assignment_in_state.places.add(place_in_state)

        place_at_headquarters = PlaceFactory()
        assignment_at_headquarters = AssignmentFactory(bureau_headquarters=True)
        assignment_at_headquarters.places.add(place_at_headquarters)

        # If it's a state, assignment_places should contain places of assignments in that state
        response = self.client.get(self.state_url)
        self.assertIn(place_in_state, response.context['assignment_places'],
                      'Assignment place in state should be returned by BureauStateDetailView for state')
        self.assertNotIn(place_at_headquarters, response.context['assignment_places'],
                      "Bureau Headquarters assignment place shouldn't be returned by BureauStateDetailView for state")

        # If it's Bureau Headquarters, assignment_places should contain places of Bureau Headquarters assignments
        response = self.client.get(self.bureau_headquarters_url)
        self.assertIn(place_at_headquarters, response.context['assignment_places'],
                      'Bureau Headquarters assignment place should be returned by BureauStateDetailView for headquarters')
        self.assertNotIn(place_in_state, response.context['assignment_places'],
                      "State assignment place shouldn't be returned by BureauStateDetailView for Bureau Headquarters")

    def test_get_context_data_assignment_places_order(self):
        """
        assignment_places should contain a list of places in that state where there was an assignment, ordering by
            1) State only
            2) Cities and counties together, sorted alphabetically
        """

        place_state_only = PlaceFactory(city=None, county=None, region=self.state)
        place_city_a = PlaceFactory(city=CityFactory(name='A'), county=None, region=self.state)
        place_county_b = PlaceFactory(city=None, county=CountyFactory(name='B'), region=self.state)
        place_city_c = PlaceFactory(city=CityFactory(name='C'), county=None, region=self.state)

        # An assignment can have multiple places - just checking place ordering here
        assignment = AssignmentFactory()
        assignment.places.add(place_county_b, place_city_a, place_state_only, place_city_c)

        response = self.client.get(self.state_url)
        self.assertListEqual(list(response.context['assignment_places']),
                             [place_state_only, place_city_a, place_county_b, place_city_c],
                             'BureauStateDetailView should return places in order of state only, then cities/counties')

    @patch.object(BureauStateDetailView, 'get_stats', autospec=True)
    def test_get_context_data_get_stats(self, mock_get_stats):
        """
        get_context_data() should fill 'stats' with return value of get_stats()
        """
        view = BureauStateDetailView()
        view.object = self.state

        mock_get_stats.return_value = 'Some stats'

        context_data = view.get_context_data()
        self.assertEqual(context_data['stats'], mock_get_stats.return_value,
                         'BureauStateDetailView.get_context_data() should call get_stats()')

    @patch('places.views.get_float_format', autospec=True)
    def test_get_stats(self, mock_get_float_format):
        """
        get_stats() should return a bunch of employee statistics for the state
        represented by BureauStateDetailView self.object
        """
        view = BureauStateDetailView()
        view.object = self.state

        # The following stats should always be returned
        expected_stats_labels = [
            'Avg. age in 1865',
            'Median age in 1865',
            '% VRC',
            '% USCT',
            '% Foreign-born',
            '% Born there',
            '% Female',
            '% Identified as "colored"',
            '% Died during assignment',
            'Former slaves',
            '% Former slaveholder',
            '% Union veterans',
            '% Confederate veterans',
            'Left-hand penmanship contest entrants'
        ]

        # AilmentType and Ailment breakdown per AilmentType should be in returned stats if present
        ailment_type_sprain = AilmentTypeFactory(name='Sprain')
        ailment_type_headache = AilmentTypeFactory(name='Headache')
        ailment_migraine_headache = AilmentFactory(name='Migraine Headache', type=ailment_type_headache)
        ailment_tension_headache = AilmentFactory(name='Tension Headache', type=ailment_type_headache)

        stats = view.get_stats()
        returned_stats_labels = list(zip(*stats))[0]

        # The following stats should always be returned
        for label in expected_stats_labels:
            self.assertIn(label, returned_stats_labels,
                          "'{}' should be returned by BureauStateDetailView.get_stats()".format(label))

        # Test AilmentType and Ailment breakdown per AilmentType
        for obj in [ailment_type_sprain, ailment_type_headache, ailment_migraine_headache, ailment_tension_headache]:
            label = '% with {}'.format(obj.name)
            self.assertIn(label, returned_stats_labels,
                          "'{}' should be returned by BureauStateDetailView.get_stats()".format(label))

        # All stats should returned in float format except the two that are counts (former slaves and left-hand
        # penmanship contest entrants), so get_float_format() should be called a certain number of times
        self.assertEqual(mock_get_float_format.call_count, len(returned_stats_labels) - 2,
                         'get_stats() should call get_float_format() for all but 2 stats')
