from django.test import TestCase

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

    def test_vrc(self):
        """
        If Employee is a member of a VRC unit, 'vrc' should be True
        """

        employee = EmployeeFactory(vrc=False)
        employee.regiments.set([RegimentFactory(vrc=True)])
        employee.save()
        employee.refresh_from_db()
        self.assertTrue(employee.vrc,
                        "Employee in VRC unit should have 'vrc' set to true after saving")
