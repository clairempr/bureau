from django.test import TestCase


from personnel.tests.factories import EmployeeFactory

from places.tests.factories import RegionFactory


class RegionTestCase(TestCase):
    """
    Test Region model
    """

    def test_percent_vrc_employees(self):
        """
        percent_vrc_employees() should return percentage of employees_employed with vrc=True
        """
        state = RegionFactory(name='Sunshine State')

        self.assertEqual(state.percent_vrc_employees(), 0,
                        "Region with no employees should have percent_vrc_employees() 0")

        employee = EmployeeFactory(vrc=False)
        employee.bureau_states.add(state)

        self.assertEqual(state.percent_vrc_employees(), 0,
                        "Region with no VRC employees should have percent_vrc_employees() 0")

        employee = EmployeeFactory(vrc=True)
        employee.bureau_states.add(state)

        self.assertEqual(state.percent_vrc_employees(), 50,
                        "Region with 50% VRC employees should have percent_vrc_employees() 50")
