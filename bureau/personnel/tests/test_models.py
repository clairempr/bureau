from django.test import TestCase

from military.tests.factories import RegimentFactory

from personnel.tests.factories import EmployeeFactory


class EmployeeTestCase(TestCase):
    """
    Test Employee model
    """

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
