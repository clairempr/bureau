from django.test import TestCase
from django.urls import reverse

from medical.tests.factories import AilmentFactory
from personnel.models import Employee
from personnel.tests.factories import EmployeeFactory
from places.tests.factories import CountryFactory, PlaceFactory, RegionFactory
from stats.views import get_places_with_pks_for_context

class DetailedViewTestCase(TestCase):
    """
    Test DetailedView
    """

    def setUp(self):
        self.url = reverse('stats:detailed')
        self.context_keys = ['average_age_in_1865', 'median_age_in_1865','average_age_at_death', 'median_age_at_death',
                    'foreign_born', 'top_birthplaces', 'ailments']

    def test_get_context_data(self):
        """
        Shouldn't cause an error if there's nothing in the database
        """
        # First test it with no data at all
        response = self.client.get(self.url)
        for key in self.context_keys:
            self.assertIn(key, response.context, "'{}' should be in context of DetailedView".format(key))

        # Now test with an Ailment but no Employees
        AilmentFactory()
        response = self.client.get(self.url)
        for key in self.context_keys:
            self.assertIn(key, response.context, "'{}' should be in context of DetailedView".format(key))

        # Test with a birthplace to see if it appears in top birthplaces
        place = PlaceFactory()
        EmployeeFactory(place_of_birth=place)
        response = self.client.get(self.url)
        self.assertIn(str(place), response.context, "Top place of birth should be in context of DetailedView")

    def test_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'stats/detailed.html')


class GeneralViewTestCase(TestCase):
    """
    Test GeneralView
    """

    def setUp(self):
        self.url = reverse('stats:general')

    def test_get_context_data(self):
        EmployeeFactory(colored=True)
        EmployeeFactory(confederate_veteran=True)
        EmployeeFactory(gender=Employee.FEMALE)
        EmployeeFactory(vrc=True)
        EmployeeFactory(vrc=True)

        response = self.client.get(self.url)
        self.assertEqual(response.context['employee_count'], 5,
                         'employee_count should be in context')

        self.assertEqual(response.context['colored_count'], 1,
                         'colored_count should be in context')
        self.assertEqual(response.context['confederate_count'], 1,
                         'confederate_count should be in context')
        self.assertEqual(response.context['female_count'], 1,
                         'female_count should be in context')
        self.assertEqual(response.context['vrc_count'], 2,
                         'vrc_count should be in context')

    def test_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'stats/general.html')


class GetPlacesWithPksForContextTestCase(TestCase):
    """
    get_places_with_pks_for_context() should take list of place names (country or region) and counts,
    get the corresponding Place, and return list of names, pks, and counts
    """

    def get_places_with_pks_for_context(self):
        PlaceFactory(country=CountryFactory(name='Canada'))
        new_york = PlaceFactory(region=RegionFactory(name='New York', country=CountryFactory(name='United States')))
        spain = PlaceFactory(country=CountryFactory(name='Spain'))

        input = [('New York', 'United States', 43), (None, 'Spain', 5)]
        expected_output = [('New York', new_york.pk, 43), ('Spain', spain.pk, 5)]

        # Compare the lists as sets because order isn't important
        self.assertSetEqual(set(get_places_with_pks_for_context(input)), set(expected_output),
                            'get_places_with_pks_for_context() should return names, pks, and counts for places from input')


class StateComparisonViewTestCase(TestCase):
    """
    Test StateComparison
    """

    def setUp(self):
        self.url = reverse('stats:state_comparison')

    def test_get_context_data(self):
        # Shouldn't cause an error if no data
        response = self.client.get(self.url)
        self.assertIsNotNone(response.context['stats'], 'stats should be in context of StateComparisonView')

        state = RegionFactory(name='Sunshine State', bureau_operations=True)
        employee = EmployeeFactory(vrc=True)
        employee.bureau_states.add(state)
        response = self.client.get(self.url)

        for label, state_set in response.context['stats']:
            if label == '% VRC employees':
                self.assertEqual(state_set[0].value, 100,
                                 "% VRC employees should be 100 if only one employee and they were VRC")
    def test_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'stats/state_comparison.html')
