from unittest.mock import patch

from django.test import SimpleTestCase, TestCase

from personnel.models import Employee
from personnel.tests.factories import EmployeeFactory
from stats.utils import get_ages_at_death, get_ages_in_year, get_mean, get_median, get_percent


class GetAgesAtDeathTestCase(TestCase):
    """
    get_ages_at_death(employees) should return list of age_at_death() for employees
    """

    @patch.object(Employee, 'age_at_death', autospec=True)
    def test_get_ages_at_death(self, mock_age_at_death):
        EmployeeFactory()
        mock_age_at_death.return_value = 37
        self.assertListEqual(get_ages_at_death(Employee.objects.all()), [37],
                             'get_ages_at_death(employees) should return age_at_death() for employees')


class GetAgesInYearTestCase(TestCase):
    """
    get_ages_in_year(employees, year) should return list of calculate_age() for employees in the given year
    """

    @patch.object(Employee, 'calculate_age', autospec=True)
    def test_get_ages_in_year(self, mock_calculate_age):
        EmployeeFactory()
        mock_calculate_age.return_value = 25
        self.assertListEqual(get_ages_in_year(Employee.objects.all(), 1865), [25],
                             'get_ages_in_year(employees, year) should return calculate_age(year) for employees')


class GetMeanTestCase(SimpleTestCase):
    """
    get_mean(data) should return the mean of the data, or 0 if there is no data
    """

    @patch('statistics.mean', autospec=True)
    def test_get_mean(self, mock_mean):
        # If no data, get_mean() should return 0
        self.assertEqual(get_mean(None), 0, 'get_mean(data) should return 0 if no data')
        self.assertEqual(get_mean([]), 0, 'get_mean(data) should return 0 if no data')

        # If there is data, get_mean() should return statistics.mean for data
        mock_mean.return_value = 42
        self.assertEqual(get_mean([1, 2, 3]), 42, 'get_mean() should return statistics.mean for data')


class GetMedianTestCase(SimpleTestCase):
    """
    get_median(data) should return the median of the data, or 0 if there is no data
    """

    @patch('statistics.median', autospec=True)
    def test_get_median(self, mock_median):
        # If no data, get_median() should return 0
        self.assertEqual(get_median(None), 0, 'get_median(data) should return 0 if no data')
        self.assertEqual(get_median([]), 0, 'get_median(data) should return 0 if no data')

        # If there is data, get_median() should return statistics.median for data
        mock_median.return_value = 42
        self.assertEqual(get_median([1, 2, 3]), 42, 'get_median() should return statistics.median for data')


class GetPercentTestCase(SimpleTestCase):
    """
    get_percent(part, total) should return the percentage that part is of total and multiply by 100, unless total is 0
    If total is 0, it should return 0
    """

    def test_get_percent(self):
        self.assertEqual(get_percent(part=50, total=100), 50, 'get_percent(part=50, total=100) should return 50')
        self.assertEqual(get_percent(part=50, total=0), 0, 'get_percent(part=50, total=0) should return 0')
