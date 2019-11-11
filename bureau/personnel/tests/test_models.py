from django.test import TestCase

from assignments.tests.factories import AssignmentFactory
from military.tests.factories import RegimentFactory
from places.tests.factories import CountryFactory, PlaceFactory

from personnel.models import Employee
from personnel.tests.factories import EmployeeFactory


class EmployeeManagerTestCase(TestCase):
    """
    Test EmployeeManager
    """

    def test_birthplace_known(self):
        """
        Should return employees with place_of_birth filled
        """

        self.assertIn(EmployeeFactory(place_of_birth=PlaceFactory()), Employee.objects.birthplace_known(),
                      "Employee with place_of_birth filled should be in Employee.objects.birthplace_known()")
        self.assertNotIn(EmployeeFactory(place_of_birth=None), Employee.objects.birthplace_known(),
                      "Employee with place_of_birth empty shouldn't be in Employee.objects.birthplace_known()")

    def test_employed_during_year(self):
        """
        Should return employees with assignments during a given year
        """

        # Employee with assignment that ended before year shouldn't be returned
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1865-08', end_date='1865-10', employee=employee)
        self.assertNotIn(employee, Employee.objects.employed_during_year(1866))
        # Check empty end date
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1865-08', employee=employee)
        self.assertNotIn(employee, Employee.objects.employed_during_year(1866))
        # Check start and end dates just year
        employee = EmployeeFactory().
        AssignmentFactory(start_date='1864', end_date='1865', employee=employee)
        self.assertNotIn(employee, Employee.objects.employed_during_year(1866))
        # Check start date just year and empty end date
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1865', employee=employee)
        self.assertNotIn(employee, Employee.objects.employed_during_year(1866))

        # Employee with assignment that started after year shouldn't be returned
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1867-08', end_date='1867-10', employee=employee)
        self.assertNotIn(employee, Employee.objects.employed_during_year(1866))
        # Check empty end date
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1867-08', employee=employee)
        self.assertNotIn(employee, Employee.objects.employed_during_year(1866))
        # Check start and end dates just year
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1867', end_date='1868', employee=employee)
        self.assertNotIn(employee, Employee.objects.employed_during_year(1866))
        # Check start date just year and empty end date
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1867', employee=employee)
        self.assertNotIn(employee, Employee.objects.employed_during_year(1866))

        # Employee with assignment that started year before and continued into that year should be returned
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1865-08', end_date='1866-10', employee=employee)
        self.assertIn(employee, Employee.objects.employed_during_year(1866))
        # Check start and end dates just year
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1865', end_date='1866', employee=employee)
        self.assertIn(employee, Employee.objects.employed_during_year(1866))

        # Employee with assignment entirely in year should be returned
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1866-08', end_date='1866-10', employee=employee)
        self.assertIn(employee, Employee.objects.employed_during_year(1866))
        # Check start date and no end date
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1866-02', employee=employee)
        self.assertIn(employee, Employee.objects.employed_during_year(1866))
        # Check start date just year and no end date
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1866', employee=employee)
        self.assertIn(employee, Employee.objects.employed_during_year(1866))

        # Employee with assignment that started that year and continued into next year should be returned
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1866-08', end_date='1867-10', employee=employee)
        self.assertIn(employee, Employee.objects.employed_during_year(1866))
        # Check start and end dates just year
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1866', end_date='1867', employee=employee)
        self.assertIn(employee, Employee.objects.employed_during_year(1866))

        # Employee with assignment that started before year and ended after year should be returned
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1865-08', end_date='1867-10', employee=employee)
        self.assertIn(employee, Employee.objects.employed_during_year(1866))
        # Check start and end dates just year
        employee = EmployeeFactory()
        AssignmentFactory(start_date='1865', end_date='1867', employee=employee)
        self.assertIn(employee, Employee.objects.employed_during_year(1866))


    def test_foreign_born(self):
        """
        Should return employees with place_of_birth filled and country code not 'US'
        """
        self.assertNotIn(EmployeeFactory(place_of_birth=None), Employee.objects.foreign_born(),
                      "Employee with place_of_birth empty shouldn't be in Employee.objects.foreign_born()")
        self.assertNotIn(EmployeeFactory(place_of_birth=PlaceFactory(country=CountryFactory(code2='US'))),
                         Employee.objects.foreign_born(),
                         "Employee with place_of_birth in 'US' shouldn't be in Employee.objects.foreign_born()")
        self.assertIn(EmployeeFactory(place_of_birth=PlaceFactory(country=CountryFactory(code2='DE'))),
                      Employee.objects.foreign_born(),
                      "Employee with place_of_birth in 'DE' should be in Employee.objects.foreign_born()")

    def test_vrc(self):
        """
        Should return employees with vrc=True
        """
        self.assertNotIn(EmployeeFactory(vrc=False), Employee.objects.vrc(),
                      "Employee with vrc=False shouldn't be in Employee.objects.vrc()")
        self.assertIn(EmployeeFactory(vrc=True),
                      Employee.objects.vrc(),
                      "Employee with vrc=True should be in Employee.objects.vrc()")

    def test_non_vrc(self):
        """
        Should return employees with vrc=False
        """
        self.assertNotIn(EmployeeFactory(vrc=True), Employee.objects.non_vrc(),
                      "Employee with vrc=True shouldn't be in Employee.objects.non_vrc()")
        self.assertIn(EmployeeFactory(vrc=False),
                      Employee.objects.non_vrc(),
                      "Employee with vrc=False should be in Employee.objects.non_vrc()")



class EmployeeTestCase(TestCase):
    """
    Test Employee model
    """

    def test_str(self):
        """
        __str__ should return Employee.last_name, Employee.first_name
        """

        employee = EmployeeFactory()
        self.assertEqual(str(employee), '{}, {}'.format(employee.last_name, employee.first_name),
                        "Employee.__str__ should be equal to Employee.last_name, Employee.first_name")

    def test_vrc_set_on_save(self):
        """
        If Employee is a member of a VRC unit, 'vrc' should be True
        """

        employee = EmployeeFactory(vrc=False)
        employee.regiments.set([RegimentFactory(vrc=True)])
        employee.save()
        employee.refresh_from_db()
        self.assertTrue(employee.vrc,
                        "Employee in VRC unit should have 'vrc' set to true after saving")
