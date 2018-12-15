import string

from django.contrib.admin import site
from django.test import RequestFactory, TestCase

from places.tests.factories import RegionFactory

from personnel.admin import EmployeeAdmin
from personnel.models import Employee
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

class FirstLetterListFilterTestCase(TestCase):
    """
    Test list filter for first letter of last name
    """

    def test_lookups(self):
        modeladmin = EmployeeAdmin(Employee, site)

        request = RequestFactory().get('/')
        changelist = modeladmin.get_changelist_instance(request)

        # Make sure that all capital letters are present in the list filter
        filterspec = changelist.get_filters(request)[0][1]
        expected = [(letter, letter) for letter in list(string.ascii_uppercase)]
        self.assertEqual(sorted(filterspec.lookup_choices), sorted(expected))
