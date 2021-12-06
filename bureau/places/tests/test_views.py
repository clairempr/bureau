from django.test import TestCase
from django.urls import reverse

from assignments.tests.factories import AssignmentFactory
from places.tests.factories import CityFactory, CountyFactory, PlaceFactory, RegionFactory

class BureauStateDetailViewTestCase(TestCase):
    """
    Test BureauStateDetail
    """

    def setUp(self):
        self.state = RegionFactory(name='Old North State')
        self.state_url = reverse('places:bureau_state_detail', kwargs={'pk': self.state.pk})
        self.bureau_headquarters = RegionFactory(bureau_headquarters=True)
        self.bureau_headquarters_url = reverse('places:bureau_state_detail', kwargs={'pk': self.bureau_headquarters.pk})
        self.context_keys = ['assignment_places', 'stats']

    def test_get_context_data(self):
        # First test it with no assignments at all
        response = self.client.get(self.state_url)
        for key in self.context_keys:
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
