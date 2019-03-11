from django.test import TestCase
from django.urls import reverse

from personnel.models import Employee
from personnel.tests.factories import EmployeeFactory

class StatisticsViewTestCase(TestCase):
    """
    Test StatisticsView
    """

    def test_get_context_data(self):
        EmployeeFactory(colored=True)
        EmployeeFactory(confederate=True)
        EmployeeFactory(gender=Employee.FEMALE)
        EmployeeFactory(vrc=True)
        EmployeeFactory(vrc=True)

        response = self.client.get(reverse('personnel:statistics'))
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
        response = self.client.get(reverse('personnel:statistics'))
        self.assertTemplateUsed(response, 'personnel/statistics.html')
