import string

from django.contrib.admin import site
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client, RequestFactory, TestCase

from military.tests.factories import RegimentFactory
from places.tests.factories import RegionFactory

from personnel.admin import EmployeeAdmin
from personnel.models import Employee
from personnel.tests.factories import EmployeeFactory


User = get_user_model()


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


    def test_save_model(self):
        """
        If Employee is a member of a VRC unit, 'vrc' should be True
        """

        # Set up superuser to log in to admin and create new Employee
        User.objects.create_superuser('admin', 'admin@example.com', 'Password123')
        self.client = Client()
        self.client.login(username='admin', password='Password123')

        # Oops, we're forgetting to set vrc to True, even though he's in a VRC unit! Hope save_model catches it...
        self.client.post(
            reverse('admin:personnel_employee_add'),
            {'last_name': 'Dodge', 'first_name': 'Charles', 'gender': 'M', 'vrc': False,
             'regiments': [RegimentFactory(vrc=True).id]},
            follow=True,
        )

        self.assertTrue(Employee.objects.first().vrc,
                "Employee in VRC unit should have 'vrc' set to true after saving")

class FirstLetterListFilterTestCase(TestCase):
    """
    Test list filter for first letter of last name
    """

    def test_lookups(self):
        employee_c = EmployeeFactory(last_name='Curren')
        employee_h = EmployeeFactory(last_name='Howard')

        modeladmin = EmployeeAdmin(Employee, site)

        request = RequestFactory().get('/')
        changelist = modeladmin.get_changelist_instance(request)

        # Make sure that all capital letters are present in the list filter
        filterspec = changelist.get_filters(request)[0][1]
        expected = [(letter, letter) for letter in list(string.ascii_uppercase)]
        self.assertEqual(sorted(filterspec.lookup_choices), sorted(expected))

        # Make sure the correct queryset is returned
        queryset = changelist.get_queryset(request)
        self.assertSetEqual(set(queryset), {employee_c, employee_h})

        # Look for employees whose last name starts with C
        request = RequestFactory().get('/', {'letter': 'C'})
        changelist = modeladmin.get_changelist_instance(request)

        # Make sure the correct queryset is returned
        queryset = changelist.get_queryset(request)
        self.assertSetEqual(set(queryset), {employee_c})
