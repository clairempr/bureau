import string

from django.contrib.admin import site
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from django.test import Client, RequestFactory, TestCase

from military.tests.factories import RegimentFactory
from places.tests.factories import RegionFactory

from personnel.admin import DateOfBirthFilledListFilter, EmployeeAdmin, FirstLetterListFilter, USCTListFilter
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
            {'id': 1, 'last_name': 'Dodge', 'first_name': 'Charles', 'gender': 'M', 'vrc': False,
             'regiments': [RegimentFactory(vrc=True).id],
             'assignments-TOTAL_FORMS': '0',
             'assignments-INITIAL_FORMS': '0',
             'assignments-MAX_NUM_FORMS': '1',
             'assignments-MIN_NUM_FORMS': '1'},
            follow=True,
        )

        self.assertTrue(Employee.objects.first().vrc,
                "Employee in VRC unit should have 'vrc' set to true after saving")


class DateOfBirthFilledListFilterTestCase(TestCase):
    """
    Test list filter for whether date_of_birth is filled
    """

    def test_lookups(self):
        employee_dob = EmployeeFactory(last_name='Howard', date_of_birth='1830-11-08')
        employee_no_dob = EmployeeFactory(last_name='Barker')

        modeladmin = EmployeeAdmin(Employee, site)
        request_factory = RequestFactory()
        user = AnonymousUser()

        request = request_factory.get('/')
        request.user = user
        changelist = modeladmin.get_changelist_instance(request)

        # Make sure that Yes and No are present in the list filter
        filter = DateOfBirthFilledListFilter(request, params='', model=Employee, model_admin=EmployeeAdmin)
        expected = [(choice, choice) for choice in ['Yes', 'No']]
        self.assertEqual(sorted(filter.lookup_choices), sorted(expected))

        # Make sure the correct queryset is returned
        queryset = changelist.get_queryset(request)
        self.assertSetEqual(set(queryset), {employee_dob, employee_no_dob})

        # Look for employees with date_of_birth filled
        request = request_factory.get('/', {'date_of_birth': 'Yes'})
        request.user = user
        changelist = modeladmin.get_changelist_instance(request)

        # Make sure the correct queryset is returned
        queryset = changelist.get_queryset(request)
        self.assertSetEqual(set(queryset), {employee_dob})

        # Look for employees with date_of_birth not filled
        request = request_factory.get('/', {'date_of_birth': 'No'})
        request.user = user
        changelist = modeladmin.get_changelist_instance(request)

        # Make sure the correct queryset is returned
        queryset = changelist.get_queryset(request)
        self.assertSetEqual(set(queryset), {employee_no_dob})


class FirstLetterListFilterTestCase(TestCase):
    """
    Test list filter for first letter of last name
    """

    def test_lookups(self):
        employee_c = EmployeeFactory(last_name='Curren')
        employee_h = EmployeeFactory(last_name='Howard')

        modeladmin = EmployeeAdmin(Employee, site)
        request_factory = RequestFactory()
        user = AnonymousUser()

        request = request_factory.get('/')
        request.user = user
        changelist = modeladmin.get_changelist_instance(request)

        # Make sure that all capital letters are present in the list filter
        filter = FirstLetterListFilter(request, params='', model=Employee, model_admin=EmployeeAdmin)
        expected = [(letter, letter) for letter in list(string.ascii_uppercase)]
        self.assertEqual(sorted(filter.lookup_choices), sorted(expected))

        # Make sure the correct queryset is returned
        queryset = changelist.get_queryset(request)
        self.assertSetEqual(set(queryset), {employee_c, employee_h})

        # Look for employees whose last name starts with C
        request = request_factory.get('/', {'letter': 'C'})
        request.user = user
        changelist = modeladmin.get_changelist_instance(request)

        # Make sure the correct queryset is returned
        queryset = changelist.get_queryset(request)
        self.assertSetEqual(set(queryset), {employee_c})


class USCTListFilterTestCase(TestCase):
    """
    Test list filter for membership in a USCT regiment
    """

    def test_lookups(self):
        usct_regiment = RegimentFactory(usct=True)
        usct_employee = EmployeeFactory(last_name='Dodge')
        usct_employee.regiments.add(usct_regiment)

        vrc_regiment = RegimentFactory(vrc=True)
        vrc_employee = EmployeeFactory(last_name='MacNulty')
        vrc_employee.regiments.add(vrc_regiment)

        modeladmin = EmployeeAdmin(Employee, site)

        request_factory = RequestFactory()
        user = AnonymousUser()

        request = request_factory.get('/')
        request.user = user
        changelist = modeladmin.get_changelist_instance(request)

        # Make sure that Yes and No are present in the list filter
        filter = USCTListFilter(request, params='', model=Employee, model_admin=EmployeeAdmin)
        expected = [(choice, choice) for choice in ['Yes', 'No']]
        self.assertEqual(sorted(filter.lookup_choices), sorted(expected))

        # Make sure the correct queryset is returned
        queryset = changelist.get_queryset(request)
        self.assertSetEqual(set(queryset), {usct_employee, vrc_employee})

        # Look for employees who were members of a USCT regiment
        request = request_factory.get('/', {'usct': 'Yes'})
        request.user = user
        changelist = modeladmin.get_changelist_instance(request)

        # Make sure the correct queryset is returned
        queryset = changelist.get_queryset(request)
        self.assertSetEqual(set(queryset), {usct_employee})

        # Look for employees who were not members of a USCT regiment
        request = request_factory.get('/', {'usct': 'No'})
        request.user = user
        changelist = modeladmin.get_changelist_instance(request)

        # Make sure the correct queryset is returned
        queryset = changelist.get_queryset(request)
        self.assertSetEqual(set(queryset), {vrc_employee})

