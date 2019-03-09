from django.test import TestCase
from django.urls import reverse

from personnel.models import Employee

class StatisticsViewTestCase(TestCase):
    """
    Test StatisticsView
    """

    def test_get_context_data(self):
      response = self.client.get(reverse('personnel:statistics'))
      self.assertEqual(response.context['employee_count'], Employee.objects.count(),
                       'employee_count should be in context')
      self.assertEqual(response.context['colored_count'], Employee.objects.filter(colored=True).count(),
                       'colored_count should be in context')
      self.assertEqual(response.context['confederate_count'], Employee.objects.filter(confederate=True).count(),
                       'confederate_count should be in context')
      self.assertEqual(response.context['female_count'], Employee.objects.filter(gender=Employee.FEMALE).count(),
                       'female_count should be in context')
      self.assertEqual(response.context['vrc_count'], Employee.objects.filter(vrc=True).count(),
                       'vrc_count should be in context')
