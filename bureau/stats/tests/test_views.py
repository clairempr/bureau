from django.test import TestCase
from django.urls import reverse

from medical.tests.factories import AilmentFactory
from personnel.models import Employee
from personnel.tests.factories import EmployeeFactory
from places.tests.factories import PlaceFactory

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
