from django.test import TestCase

from places.tests.factories import RegionFactory

from personnel.admin import EmployeeAdmin
from personnel.tests.factories import EmployeeFactory


class EmployeeAdminTestCase(TestCase):
    """
    Test custom EmployeeAdmin functionality
    """

    def test_bureau_state(self):
        """
        Field bureau_state should contain a
        list of Employee's bureau_states
        """

        state1 = RegionFactory(name='Lower Alabama')
        state2 = RegionFactory(name='Old Virginny')
        state3 = RegionFactory(name='Sunshine State')
        states = [state1, state2]

        employee = EmployeeFactory()
        employee.bureau_states.set(states)

        for state in states:
            self.assertIn(state.name, EmployeeAdmin.bureau_state(EmployeeAdmin, employee),
                          'State in Employee.bureau_states should be in EmployeeAdmin.bureau_state')
        self.assertNotIn(state3.name, EmployeeAdmin.bureau_state(EmployeeAdmin, employee),
                         'State not in Employee.bureau_states should not be in EmployeeAdmin.bureau_state')
